import matplotlib
# Use a non-interactive backend to avoid macOS GUI errors in server context
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import torch
import torch.nn.functional as F
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
import os, urllib.request
import torchvision.transforms as tf
from transformers import AutoImageProcessor, AutoModelForImageClassification, pipeline

TOP_N = 10

def count_objects(image_path, item_type):
    image = Image.open(image_path)
    height, width = image.size[1], image.size[0]
    # Derive a base name from the uploaded image for any derived outputs we save
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    checkpoint_path = os.path.join(os.path.dirname(__file__), 'sam_vit_b_01ec64.pth')
    if not os.path.exists(checkpoint_path):
        url = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
        urllib.request.urlretrieve(url, checkpoint_path)

    sam = sam_model_registry["vit_b"](checkpoint=checkpoint_path)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    sam.to(device)

    mask_generator = SamAutomaticMaskGenerator(
        model=sam,
        points_per_side=16,
        pred_iou_thresh=0.7,
        stability_score_thresh=0.85,
        min_mask_region_area=500,
    )
   
    image_np = np.array(image).astype(np.float32)
    masks = mask_generator.generate(image_np)
    #masks = mask_generator.generate(np.array(image))
    masks_sorted = sorted(masks, key=lambda x: x['area'], reverse=True)

    predicted_panoptic_map = np.zeros((height, width), dtype=np.int32)
    for idx, mask_data in enumerate(masks_sorted[:TOP_N]):
        predicted_panoptic_map[mask_data['segmentation']] = idx + 1

    # Save a side-by-side visualization (Original + Segmentation) next to the input image
    try:
        seg_filename = f"{base_name}_seg.png"
        seg_abs_path = os.path.join(os.path.dirname(image_path), seg_filename)

        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        plt.imshow(image)
        plt.title('Original Image')
        plt.axis('off')

        plt.subplot(1, 2, 2)
        plt.imshow(predicted_panoptic_map, cmap='tab20', interpolation='nearest')
        plt.title(f'SAM Segmentation ({len(masks_sorted[:TOP_N])} segments)')
        plt.axis('off')

        plt.tight_layout()
        plt.savefig(seg_abs_path, bbox_inches='tight', dpi=150)
        plt.close()
    except Exception:
        # If saving fails for any reason, continue without blocking the flow
        seg_filename = None

    # Convert to tensor for downstream processing
    predicted_panoptic_map = torch.from_numpy(predicted_panoptic_map)

    transform = tf.Compose([tf.PILToTensor()])
    img_tensor = transform(image)

    def get_mask_box(tensor: torch.Tensor) -> tuple:
        non_zero_indices = torch.nonzero(tensor, as_tuple=True)[0]
        if non_zero_indices.shape[0] == 0:
            return None, None
        first_n = non_zero_indices[:1].item()
        last_n = non_zero_indices[-1:].item()
        return first_n, last_n

    segments = []
    for label in predicted_panoptic_map.unique():
        y_start, y_end = get_mask_box(predicted_panoptic_map==label)
        x_start, x_end = get_mask_box((predicted_panoptic_map==label).T)
        cropped_tensor = img_tensor[:, y_start:y_end+1, x_start:x_end+1]
        cropped_mask = predicted_panoptic_map[y_start:y_end+1, x_start:x_end+1] == label
        segment = cropped_tensor * cropped_mask.unsqueeze(0)
        segment[:, ~cropped_mask] = 188
        segments.append(segment)

    image_processor = AutoImageProcessor.from_pretrained("microsoft/resnet-50")
    class_model = AutoModelForImageClassification.from_pretrained("microsoft/resnet-50")
    predicted_classes = []
    for segment in segments:
        inputs = image_processor(images=segment, return_tensors="pt")
        outputs = class_model(**inputs)
        logits = outputs.logits
        predicted_class_idx = logits.argmax(-1).item()
        predicted_class = class_model.config.id2label[predicted_class_idx]
        predicted_classes.append(predicted_class)

    label_classifier = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")
    candidate_labels = [
        "car",
        "cat",
        "tree",
        "dog",
        "building",
        "person",
        "sky",
        "ground",
        "hardware",
    ]
    labels = []
    for predicted_class in predicted_classes:
        result = label_classifier(predicted_class, candidate_labels=candidate_labels)
        label = result['labels'][0]
        labels.append(label)

    # Save images for segments whose label matches the requested item_type
    matched_segment_filenames: list[str] = []
    matched_segments_meta: list[dict] = []
    merged_matches_filename = None
    try:
        for idx, (segment, label, pclass) in enumerate(zip(segments, labels, predicted_classes)):
            if label != item_type:
                continue
            # Convert tensor (C,H,W) to uint8 numpy (H,W,C)
            seg_np = segment.detach().cpu().permute(1, 2, 0).numpy()
            seg_np = np.clip(seg_np, 0, 255).astype(np.uint8)
            seg_img = Image.fromarray(seg_np)
            match_filename = f"{base_name}_match_{idx}.png"
            match_abs_path = os.path.join(os.path.dirname(image_path), match_filename)
            seg_img.save(match_abs_path)
            matched_segment_filenames.append(match_filename)
            matched_segments_meta.append({
                'filename': match_filename,
                'label': label,
                'predicted_class': pclass
            })
        # Build a merged composite image out of the matched segments to have a single URL
        if len(matched_segment_filenames) > 0:
            # Reserve extra vertical space above each tile for caption text
            tile_w = 224
            tile_img_h = 224
            caption_h = 28
            tile_h = tile_img_h + caption_h
            cols = min(3, max(1, len(matched_segment_filenames)))
            rows = (len(matched_segment_filenames) + cols - 1) // cols
            merged = Image.new('RGB', (cols * tile_w, rows * tile_h), color=(245, 245, 247))
            draw = ImageDraw.Draw(merged)
            try:
                font = ImageFont.load_default()
            except Exception:
                font = None
            for i, fname in enumerate(matched_segment_filenames):
                try:
                    pth = os.path.join(os.path.dirname(image_path), fname)
                    im = Image.open(pth).convert('RGB')
                    im.thumbnail((tile_w, tile_img_h), Image.Resampling.LANCZOS)
                    # Compute tile origin
                    cell_x = (i % cols) * tile_w
                    cell_y = (i // cols) * tile_h
                    # Paste image centered within image area (below caption area)
                    x = cell_x + (tile_w - im.width) // 2
                    y = cell_y + caption_h + (tile_img_h - im.height) // 2
                    merged.paste(im, (x, y))
                    # Prepare caption (label: predicted_class) above the image
                    meta = matched_segments_meta[i]
                    caption = f"{meta.get('label','')}: {meta.get('predicted_class','')}"
                    if font:
                        # Center caption horizontally in its tile
                        try:
                            bbox = draw.textbbox((0,0), caption, font=font)
                            text_w = bbox[2]-bbox[0]
                            text_h = bbox[3]-bbox[1]
                        except Exception:
                            text_w = len(caption) * 6
                            text_h = 10
                        tx = cell_x + (tile_w - text_w)//2
                        # Vertically center within caption area (with small top padding)
                        ty = cell_y + max(0, (caption_h - text_h)//2)
                        try:
                            draw.text((tx, ty), caption, fill=(0,0,0), font=font, stroke_width=2, stroke_fill=(255,255,255))
                        except TypeError:
                            draw.text((tx+1, ty+1), caption, fill=(255,255,255), font=font)
                            draw.text((tx, ty), caption, fill=(0,0,0), font=font)
                except Exception:
                    continue
            merged_matches_filename = f"{base_name}_matches.png"
            merged_abs_path = os.path.join(os.path.dirname(image_path), merged_matches_filename)
            merged.save(merged_abs_path)
    except Exception:
        # Non-fatal if saving any matched segment fails
        matched_segment_filenames = []
        matched_segments_meta = []
        merged_matches_filename = None

    count = sum(1 for label in labels if label == item_type)
    return {
        'count': count,
        'labels': labels,
        'segments': len(segments),
        # Return the saved segmentation file name so the API layer can expose a URL
        'segmentation_filename': seg_filename,
        # Return filenames of matched per-segment images
    'matched_segment_filenames': matched_segment_filenames,
    # Include meta (label + predicted_class) for each matched segment
    'matched_segments': matched_segments_meta,
    # Also return a single merged composite filename for easy UI display
    'matched_segments_merged_filename': merged_matches_filename
    }
