
import matplotlib.pyplot as plt
from PIL import Image
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

    count = sum(1 for label in labels if label == item_type)
    return {
        'count': count,
        'labels': labels,
        'segments': len(segments)
    }
