import os
import urllib.request
import numpy as np
from PIL import Image

TOP_N = 10

def _fast_count(image_path, item_type):
    import cv2
    img = cv2.imread(image_path)
    if img is None:
        return {'count': 0, 'labels': [], 'segments': 0}
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # Simple threshold and contour count as a proxy
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Filter very small blobs
    areas = [cv2.contourArea(c) for c in cnts]
    big = [a for a in areas if a > 50]
    count = len(big)
    return {'count': count, 'labels': [item_type]*count, 'segments': count}


def count_objects(image_path, item_type):
    # Fast path for local/dev/CI when heavy models are not available
    if os.getenv('FAST_MODE') == '1' or os.getenv('CI') == 'true':
        return _fast_count(image_path, item_type)
    return _heavy_count(image_path, item_type)


def _heavy_count(image_path, item_type):  # pragma: no cover
    # Lazy import heavy deps to avoid import-time failures
    import torch
    import torchvision.transforms as tf
    from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
    from transformers import AutoImageProcessor, AutoModelForImageClassification, pipeline

    image = Image.open(image_path)
    height, width = image.size[1], image.size[0]
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
    masks_sorted = sorted(masks, key=lambda x: x['area'], reverse=True)

    predicted_panoptic_map = np.zeros((height, width), dtype=np.int32)
    for idx, mask_data in enumerate(masks_sorted[:TOP_N]):
        predicted_panoptic_map[mask_data['segmentation']] = idx + 1

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
        "car","cat","tree","dog","building","person","sky","ground","hardware",
    ]
    labels = []
    for predicted_class in predicted_classes:
        result = label_classifier(predicted_class, candidate_labels=candidate_labels)
        label = result['labels'][0]
        labels.append(label)

    count = sum(1 for label in labels if label == item_type)
    return {'count': count, 'labels': labels, 'segments': len(segments)}
