import sys
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog, QGridLayout, QListWidget, QMessageBox, QHBoxLayout, QInputDialog, QApplication
from PyQt5.QtGui import QPixmap
import os
from PyQt5.QtCore import Qt, QCoreApplication
import json


def get_labels(dir_path):
    p = os.path.join(dir_path, "labels.json")

    if os.path.exists(p):
        with open(p, "r") as f:
            data = json.load(f)
        f.close()
        return data
    else:
        data = {}
        with open(p, "w") as file:
            json.dump(data, file, indent=4)
        return None


class LabelingTool(QMainWindow):
    def __init__(self, aspect_ratio=16 / 9, img_height=400):
        super().__init__()
        self.setWindowTitle("Labeling Tool")

        # Create the main widget and layout
        self.main_widget = QWidget(self)
        self.main_layout = QGridLayout(self.main_widget)

        self.left_top_widget = QWidget(self)
        self.left_top_layout = QVBoxLayout(self.left_top_widget)
        self.main_layout.addWidget(self.left_top_widget, 0, 0, 3, 1)

        self.right_top_widget = QWidget(self)
        self.right_top_layout = QVBoxLayout(self.right_top_widget)
        self.main_layout.addWidget(self.right_top_widget, 0, 2, 1, 1)

        self.file_list = QListWidget(self)
        self.file_list.setFixedSize(img_height//2, img_height)
        self.file_list.itemSelectionChanged.connect(self.load_selected_image)
        # Add the list widget at row 0, column 1, spanning 2 rows and 1 column
        self.right_top_layout.addWidget(self.file_list)

        # Create a label to display the image or object to be labeled
        self.current_image_label = QLabel(self)
        self.left_top_layout.addWidget(self.current_image_label)

        self.index_label = QLabel(self)
        self.right_top_layout.addWidget(self.index_label)

        self.bottom_widget = QWidget(self)
        self.bottom_layout = QGridLayout(self.bottom_widget)
        self.main_layout.addWidget(self.bottom_widget, 3, 0, 1, 2)

        self.previous_label_1 = QLabel(self)
        self.previous_label_2 = QLabel(self)

        self.next_label_1 = QLabel(self)
        self.next_label_2 = QLabel(self)

        self.bottom_layout.addWidget(self.previous_label_2, 0, 0)
        self.bottom_layout.addWidget(self.previous_label_1, 0, 1)

        self.bottom_layout.addWidget(self.next_label_1, 0, 2)
        self.bottom_layout.addWidget(self.next_label_2, 0, 3)

        self.bottom_layout.addWidget(QLabel("Previous Image 2"), 1, 0)
        self.bottom_layout.addWidget(QLabel("Previous Image 1"), 1, 1)
        self.bottom_layout.addWidget(QLabel("Next Image 1"), 1, 2)
        self.bottom_layout.addWidget(QLabel("Next Image 2"), 1, 3)

        # Create a button for getting the list of images
        self.get_images_button = QPushButton("Get Images", self)
        self.get_images_button.clicked.connect(self.get_images)
        self.get_images_button.setFixedSize(100, 50)
        self.right_top_layout.addWidget(self.get_images_button)

        # Create buttons for moving to previous and next images
        self.previous_button = QPushButton("Previous (q)", self)
        self.previous_button.clicked.connect(self.load_previous_image)
        self.previous_button.setFixedSize(100, 50)
        self.right_top_layout.addWidget(self.previous_button)

        self.next_button = QPushButton("Next (e)", self)
        self.next_button.clicked.connect(self.load_next_image)
        self.next_button.setFixedSize(100, 50)
        self.right_top_layout.addWidget(self.next_button)

        self.save_button = QPushButton("Save (ctrl+s)", self)
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_data)
        self.save_button.setFixedSize(100, 50)
        self.right_top_layout.addWidget(self.save_button)

        # Initialize image list and current index
        self.image_paths = []
        self.current_index = -1
        self.label_data = {}

        self.label_root_dir = ""

        self.main_layout.setColumnStretch(0, 1)  # First column stretches
        self.main_layout.setColumnStretch(1, 2)  # Second column stretches
        # Set the main widget and layout for the main window
        self.main_layout.setRowStretch(0, 1)  # First row stretches
        # self.main_layout.addWidget(self.left_top_widget, 0, 0)  # Add left section to the first column
        # self.main_layout.addWidget(self.right_top_widget, 0, 2)

        self.setCentralWidget(self.main_widget)
        self.ratio = aspect_ratio
        self.img_height = img_height

        # self.current_label.setFixedSize(int(self.ratio * self.img_height), self.img_height)
        # self.previous_label_1.setFixedSize(int(self.ratio * self.img_height // 2), self.img_height//2)
        # self.previous_label_2.setFixedSize(int(self.ratio * self.img_height // 2), self.img_height//2)
        # self.next_label_1.setFixedSize(int(self.ratio * self.img_height // 2), self.img_height // 2)
        # self.next_label_2.setFixedSize(int(self.ratio * self.img_height // 2), self.img_height // 2)

    def save_data(self):
        print("SAVED")
        p = os.path.join(self.label_root_dir, "labels.json")
        with open(p, "w") as file:
            json.dump(self.label_data, file, indent=4)
        file.close()

    def load_image(self, cur_idx):
        # Load the image and display it on the label
        image_path = self.image_paths[cur_idx]
        try:
            _id = os.path.basename(image_path)
            cur_label = self.label_data[_id]
        except KeyError:
            cur_label = "No Label"

        cur_image = QPixmap(image_path)
        # self.left_top_widget.setPixmap(cur_image.scaled(400, 300))
        self.current_image_label.setPixmap(cur_image.scaled(int(self.ratio * 400), 400))

        current_order = cur_idx + 1
        total_files = len(self.image_paths)
        self.index_label.setText(f"File: {current_order}/{total_files}, Class: {cur_label}")

        prev_1 = (cur_idx - 1) % len(self.image_paths)
        prev_2 = (cur_idx - 2) % len(self.image_paths)
        next_1 = (cur_idx + 1) % len(self.image_paths)
        next_2 = (cur_idx + 2) % len(self.image_paths)

        previous_image_1 = QPixmap(self.image_paths[prev_1])
        self.previous_label_1.setPixmap(previous_image_1.scaled(int(self.ratio * 100), 100))

        previous_image_2 = QPixmap(self.image_paths[prev_2])
        self.previous_label_2.setPixmap(previous_image_2.scaled(int(self.ratio * 100), 100))

        next_image_1 = QPixmap(self.image_paths[next_1])
        self.next_label_1.setPixmap(next_image_1.scaled(int(self.ratio * 100), 100))

        next_image_2 = QPixmap(self.image_paths[next_2])
        self.next_label_2.setPixmap(next_image_2.scaled(int(self.ratio * 100), 100))

    def get_images(self):
        # Open a file dialog to select multiple image files
        folder_dialog = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        # print(os.path.dirname(os.path.abspath(folder_dialog)))

        if folder_dialog:
            # Get all image files from the selected folder
            image_files = [file for file in os.listdir(folder_dialog) if file.lower().endswith(('.png', '.jpg', '.jpeg'))]
            image_files.sort()
            self.image_paths = [os.path.join(folder_dialog, file) for file in image_files]
            self.current_index = -1
            label_dir = os.path.dirname(os.path.abspath(folder_dialog))
            self.label_root_dir = label_dir
            label_data = get_labels(label_dir)
            self.save_button.setEnabled(True)
            if label_data:
                self.label_data = label_data
            else:
                print(f"Created a new empty labeling file onto '{label_dir}/labels.json'")

            self.load_next_image()

            self.file_list.clear()
            for image_file in image_files:
                self.file_list.addItem(image_file)

            self.remove_buttons()

    def remove_buttons(self):
        self.get_images_button.hide()

    def load_next_image(self):
        if self.image_paths:
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self.load_image(self.current_index)

    def load_previous_image(self):
        if self.image_paths:
            self.current_index = (self.current_index - 1) % len(self.image_paths)
            self.load_image(self.current_index)

    def update_index_label(self):
        self.get_num_images()

        if self.n_images > 0:
            current_order = self.current_index + 1
            self.index_label.setText(f"Image: {current_order}/{self.n_images}")
        else:
            self.index_label.setText("")

    def load_selected_image(self):
        selected_item = self.file_list.currentItem()
        if selected_item is not None:
            selected_index = self.file_list.row(selected_item)
            self.load_image(selected_index)

    def modify_class_label(self, class_label):

        if 0 <= self.current_index < len(self.image_paths):
            # Update the class label for the current image

            filename = os.path.basename(self.image_paths[self.current_index])
            self.label_data[filename] = str(class_label)

            # Update the index label to display the updated class label
            # current_order = self.current_index + 1
            # total_files = len(self.image_paths)
            # self.index_label.setText(f"File: {current_order}/{total_files}, Class: {class_label}")

    def keyPressEvent(self, event):
        # This method is the overriding of the keyPressEvent for QMainWindow
        if event.key() == Qt.Key_E:  # Move to next image when "r" key is pressed
            self.load_next_image()
        elif event.key() == Qt.Key_Q:  # Move to previous image when "q" key is pressed
            self.load_previous_image()
        elif event.key() == Qt.Key_R:
            reply = QMessageBox.question(self, 'Message', "Do you want to modify the class of this image ?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                class_input, ok = QInputDialog.getText(self, "Modify Class", "Enter the new class:")
                if ok:
                    self.modify_class_label(class_input.strip())
                    # self.right_top_widget.refresh_widget()
            else:
                event.ignore()

        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_S:
            self.save_data()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    labeling_tool = LabelingTool()
    QCoreApplication.instance().aboutToQuit.connect(labeling_tool.save_data)
    labeling_tool.show()
    sys.exit(app.exec_())
