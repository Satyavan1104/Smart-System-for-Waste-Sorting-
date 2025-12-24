import os

# Define the mapping of subclasses to parent classes
class_mapping = {
    0: 2,  # newspaper -> recyclable (class 0)
    1: 2,  # cardboard -> recyclable (class 0)
    2: 2,  # glass jars -> recyclable (class 0)
    3: 2,  # plastic -> recyclable (class 0)
    4: 2,  # steel tins -> recyclable (class 0)
    5: 1,  # batteries -> non-recyclable (class 1)
    6: 1,
    7: 1,  # batteries -> non-recyclable (class 1)
    8: 1,  # alkaline batteries -> non-recyclable (class 1)
    9: 1,  # batteries -> non-recyclable (class 1)
    10: 1,
    11: 1,  # batteries -> non-recyclable (class 1)
    12: 1,
    13: 0,  # batteries -> non-recyclable (class 1)
    14: 0,
    15: 0,  # batteries -> non-recyclable (class 1)
    16: 0,  # alkaline batteries -> non-recyclable (class 1)
    17: 0,  # batteries -> non-recyclable (class 1)
    18: 0, # Add more mappings as needed
}

# Path to your labels directory
labels_dir = "C:/Users/Monica/Desktop/w/waste.v3i.yolov5pytorch/valid/labels"

# Iterate through all label files
for filename in os.listdir(labels_dir):
    if filename.endswith(".txt"):
        file_path = os.path.join(labels_dir, filename)
        with open(file_path, "r") as file:
            lines = file.readlines()

        # Update class IDs
        updated_lines = []
        for line in lines:
            parts = line.strip().split()
            class_id = int(parts[0])
            if class_id in class_mapping:
                parts[0] = str(class_mapping[class_id])
                updated_lines.append(" ".join(parts))

        # Overwrite the file with updated annotations
        with open(file_path, "w") as file:
            file.write("\n".join(updated_lines))

print("Class merging complete!")
