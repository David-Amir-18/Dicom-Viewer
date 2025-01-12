import os
import pydicom
import numpy as np
from PyQt5.QtGui import QPixmap, QPainter, QColor, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QPushButton, QVBoxLayout, QWidget,
    QTextEdit, QSlider, QLabel, QInputDialog, QLineEdit, QMessageBox, QHBoxLayout, QGridLayout, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer, QPoint, QSize
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.colors import rgb2hex
from matplotlib.figure import Figure

# TileViewer for 3d files 
class TileViewer(QMainWindow):
    def __init__(self, frames):
        super().__init__()
        self.setWindowTitle("3D DICOM Tile Viewer")
        self.setGeometry(150, 150, 1000, 800)  # Larger default window size

        # Scrollable area for tiles
        scroll_area = QScrollArea()
        container_widget = QWidget()
        scroll_area.setWidget(container_widget)
        scroll_area.setWidgetResizable(True)

        # Grid layout for tiles
        grid_layout = QGridLayout(container_widget)
        grid_layout.setHorizontalSpacing(10)
        grid_layout.setVerticalSpacing(10)
        grid_layout.setContentsMargins(10, 10, 10, 10)  # Minimal margins for compact layout

        # Display all frames as enhanced tiles
        rows = int(np.ceil(np.sqrt(len(frames))))
        cols = rows

        for idx, frame in enumerate(frames):
            # Create a figure for each tile
            figure = Figure(figsize=(6, 6), dpi=100)  # Larger tile size
            canvas = FigureCanvas(figure)
            ax = figure.add_subplot(111)

            # Display the DICOM frame
            ax.imshow(frame, cmap="gray", interpolation="nearest")
            ax.axis("off")  # Remove axes for a cleaner look
            ax.margins(0)  # Remove margins around the image
            ax.set_title(f"Slice {idx + 1}", fontsize=12, pad=10)  # Add titles with padding

            # Adjust canvas size
            canvas.setMinimumSize(300, 300)  # Ensure large tiles
            grid_layout.addWidget(canvas, idx // cols, idx % cols)

        # Set container layout
        self.setCentralWidget(scroll_area)
class DicomViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Team##9 Dicom Viewer")
        self.setGeometry(100, 100, 600, 800)
        self.dicom_file = None
        self.dicom_files = []  # List to store multiple DICOM files
        self.slices = []  # List to store image slices
        self.current_slice_index = 0
        self.initUI()
        self.playing_state = True
        self.timer = QTimer(self)
        self.isM2DOr3DFile = False
        self.frames = None
        self.current_frame_index = 0
        self.timerm2d = QTimer()
        self.timerm2d.timeout.connect(self.next_frame)


    def display_frame(self, frame):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if frame.shape[-1] == 3:  # RGB data
            ax.imshow(frame)
        else:  # Grayscale data
            ax.imshow(frame, cmap="gray")
        ax.axis("off")
        self.canvas.draw()


    def play_video(self):
        if self.frames is not None:
            self.timerm2d.start(100)  # Adjust delay as needed (milliseconds)

    def stop_video(self):
        self.timerm2d.stop()

    def next_frame(self):
        if self.frames is not None:
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
            self.display_frame(self.frames[self.current_frame_index])


    def create_play_icon(self):
        # Create a green play icon
        pixmap = QPixmap(30, 30)
        pixmap.fill(Qt.transparent)  # Fill with transparent background
        painter = QPainter(pixmap)
        painter.setBrush(QColor(9, 132, 227))  # Set brush color to rgb(9, 132, 227)
        painter.setPen(Qt.transparent)  # No outline
        # Draw a play triangle
        triangle = [QPoint(5, 5), QPoint(25, 15), QPoint(5, 25)]
        painter.drawConvexPolygon(*triangle)  # Use drawConvexPolygon to draw the triangle
        painter.end()
        return QIcon(pixmap)  # Return as QIcon

    def create_pause_icon(self):
        # Create a pause icon (two vertical bars)
        pixmap = QPixmap(30, 30)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setBrush(QColor(255, 0, 0))  # Set brush color to green
        painter.setPen(Qt.transparent)  # No outline
        # Draw two vertical bars for pause
        painter.drawRect(10, 5, 5, 20)
        painter.drawRect(20, 5, 5, 20)
        painter.end()
        return QIcon(pixmap)  # Return as QIcon

    def toggle_play(self):
        # Toggle play/pause for the specified view

        if self.playing_state:
            self.playing_state = False
            self.play_button.setIcon(self.create_pause_icon())
            if self.isM2DOr3DFile:
                self.play_video()

        else:

            self.playing_state = True
            self.play_button.setIcon(self.create_play_icon())
            if self.isM2DOr3DFile:
              self.stop_video()
        # Logic to start/stop playing XY view slices goes here

    def rgb_to_hex(self, rgb):
        """Convert an RGB tuple to a HEX string."""
        return '#' + ''.join(f'{c:02x}' for c in rgb)

    def open_tile_viewer(self, frames):
        self.tile_viewer = TileViewer(frames)
        self.tile_viewer.show()

    def initUI(self):
        layout = QVBoxLayout()

        # Buttons
        self.openButton = QPushButton("Open DICOM File")
        self.openButton.clicked.connect(self.open_file)
        layout.addWidget(self.openButton)


        self.viewTagsButton = QPushButton("View All DICOM Tags")
        self.viewTagsButton.clicked.connect(self.view_tags)
        layout.addWidget(self.viewTagsButton)

        # Horizontal Layout for Specific Data Buttons
        self.sectionButtonsLayout = QHBoxLayout()
        self.metaButton = QPushButton("Meta")
        self.metaButton.clicked.connect(self.view_meta_information)
        self.sectionButtonsLayout.addWidget(self.metaButton)

        self.patientButton = QPushButton("Patient")
        self.patientButton.clicked.connect(self.view_patient_information)
        self.sectionButtonsLayout.addWidget(self.patientButton)

        self.studyButton = QPushButton("Study")
        self.studyButton.clicked.connect(self.view_study_information)
        self.sectionButtonsLayout.addWidget(self.studyButton)

        self.seriesButton = QPushButton("Series")
        self.seriesButton.clicked.connect(self.view_series_information)
        self.sectionButtonsLayout.addWidget(self.seriesButton)

        self.imageButton = QPushButton("Image")
        self.imageButton.clicked.connect(self.view_image_information)
        self.sectionButtonsLayout.addWidget(self.imageButton)

        self.equipmentButton = QPushButton("Equipment")
        self.equipmentButton.clicked.connect(self.view_equipment_information)
        self.sectionButtonsLayout.addWidget(self.equipmentButton)

        self.privateButton = QPushButton("Private")
        self.privateButton.clicked.connect(self.view_private_information)
        self.sectionButtonsLayout.addWidget(self.privateButton)

        self.otherButton = QPushButton("Other")
        self.otherButton.clicked.connect(self.view_other_information)
        self.sectionButtonsLayout.addWidget(self.otherButton)

        layout.addLayout(self.sectionButtonsLayout)

        self.searchButton = QPushButton("Search in Tags")
        self.searchButton.clicked.connect(self.search_tag)
        layout.addWidget(self.searchButton)

        self.anonymizeButton = QPushButton("Anonymize DICOM File")
        self.anonymizeButton.clicked.connect(self.anonymize_dicom)
        layout.addWidget(self.anonymizeButton)

        self.prefixInput = QLineEdit()
        self.prefixInput.setPlaceholderText("Enter prefix for anonymization (default: Anon)")
        layout.addWidget(self.prefixInput)

        # Slice Navigation Slider




        self.play_button = QPushButton()
        self.play_button.setIcon(self.create_play_icon())  # Use custom green play icon
        self.play_button.setIconSize(QSize(30, 20))  # Set icon size
        self.play_button.setFixedHeight(25)
        self.play_button.clicked.connect(lambda: self.toggle_play())
        layout.addWidget(self.play_button)
        rgb_color = (9, 132, 227)

        # Image Display
        self.figure = Figure(edgecolor=self.rgb_to_hex(rgb_color))
        self.figure.patch.set_linewidth(1)
        self.figure.patch.set_facecolor('#000000')

        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("border: 1px solid rgb(9, 132, 227);; background-color: black;")
        layout.addWidget(self.canvas)

        # DICOM Tags Display
        self.tagsDisplay = QTextEdit()
        self.tagsDisplay.setReadOnly(True)
        self.tagsDisplay.setPlaceholderText("DICOM tags will appear here...")
        self.tagsDisplay.setMinimumHeight(200)
        layout.addWidget(self.tagsDisplay)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open DICOM File", "", "DICOM Files (*.dcm)")
        if file_path:
            try:
                self.dicom_file = pydicom.dcmread(file_path)

                if hasattr(self.dicom_file, "PixelData"):
                    # Extract pixel data
                    pixel_data = self.dicom_file.pixel_array
                print(len(pixel_data.shape))
                if len(pixel_data.shape) == 4:  # M2D with multiple frames
                        self.frames = pixel_data
                        self.current_frame_index = 0

                        self.display_frame(self.frames[self.current_frame_index])
                        self.isM2DOr3DFile = True
                        self.tagsDisplay.setPlainText(
                            "M2D DICOM file loaded successfully. Use 'View All DICOM Tags' to see details.")

                if len(pixel_data.shape) == 3: #3d file
                    self.frames = pixel_data
                    self.open_tile_viewer(self.frames)
                    self.current_frame_index = 0
                    self.isM2DOr3DFile = True
                    self.display_frame(self.frames[self.current_frame_index])
                    self.tagsDisplay.setPlainText(
                        "3D DICOM file loaded successfully. Use 'View All DICOM Tags' to see details.")

                elif len(pixel_data.shape) == 2:  # Single 2D image with color channels
                        self.frames = [pixel_data]
                        self.isM2DOr3DFile = False
                        self.slices = [self.dicom_file.pixel_array]  # Load a single slice
                        self.display_image(self.slices[0])
                        self.tagsDisplay.setPlainText(
                        "Single 2D DICOM file loaded successfully. Use 'View All DICOM Tags' to see details.")
            except Exception as e:
                self.tagsDisplay.setPlainText(f"Failed to load DICOM file: {e}")


    def display_image(self, image_data):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.imshow(image_data, cmap="gray")
        ax.axis("off")
        self.canvas.draw()

    def view_tags(self):
        if  self.dicom_file:  # Single file mode
            tags_text = ""
            for element in self.dicom_file:
                if element.keyword == "PixelData":
                    continue
                if element.keyword and element.value:
                    tags_text += f"{element.keyword}: {element.value}\n"

            self.tagsDisplay.setPlainText(tags_text)
        else:
            self.tagsDisplay.setPlainText("No DICOM file or folder loaded.")

    def view_meta_information(self):
        """Display File Meta Information."""
        tags_text = "File Meta Information:\n" + "-" * 50 + "\n"
        if self.dicom_file and self.dicom_file.file_meta:
            for element in self.dicom_file.file_meta:
                if element.keyword and element.value:
                    tags_text += f"{element.keyword}: {element.value}\n"
        else:
            tags_text += "No meta information available.\n"
        self.tagsDisplay.setPlainText(tags_text)

    def view_patient_information(self):
        """Display Patient Information."""
        tags_text = "Patient Information:\n" + "-" * 50 + "\n"
        if self.dicom_file:
            for element in self.dicom_file:
                if element.keyword in ["PatientName", "PatientID", "PatientBirthDate", "PatientSex"] and element.value:
                    tags_text += f"{element.keyword}: {element.value}\n"
        else:
            tags_text += "No patient information available.\n"
        self.tagsDisplay.setPlainText(tags_text)

    def view_study_information(self):
        """Display Study Information."""
        tags_text = "Study Information:\n" + "-" * 50 + "\n"
        if self.dicom_file:
            for element in self.dicom_file:
                if element.keyword in ["StudyInstanceUID", "StudyDate", "StudyTime", "ReferringPhysicianName",
                                       "AccessionNumber"] and element.value:
                    tags_text += f"{element.keyword}: {element.value}\n"
        else:
            tags_text += "No study information available.\n"
        self.tagsDisplay.setPlainText(tags_text)

    def view_series_information(self):
        """Display Series Information."""
        tags_text = "Series Information:\n" + "-" * 50 + "\n"
        if self.dicom_file:
            for element in self.dicom_file:
                if element.keyword in ["SeriesInstanceUID", "SeriesNumber", "Modality"] and element.value:
                    tags_text += f"{element.keyword}: {element.value}\n"
        else:
            tags_text += "No series information available.\n"
        self.tagsDisplay.setPlainText(tags_text)

    def view_image_information(self):
        """Display Image Information."""
        tags_text = "Image Information:\n" + "-" * 50 + "\n"
        if self.dicom_file:
            for element in self.dicom_file:
                if element.keyword in ["InstanceNumber", "ImagePositionPatient", "ImageOrientationPatient",
                                       "PixelSpacing", "SliceThickness"] and element.value:
                    tags_text += f"{element.keyword}: {element.value}\n"
        else:
            tags_text += "No image information available.\n"
        self.tagsDisplay.setPlainText(tags_text)

    def view_equipment_information(self):
        """Display Equipment Information."""
        tags_text = "Equipment Information:\n" + "-" * 50 + "\n"
        if self.dicom_file:
            for element in self.dicom_file:
                if element.keyword in ["Manufacturer", "ManufacturerModelName", "SoftwareVersions",
                                       "DeviceSerialNumber"] and element.value:
                    tags_text += f"{element.keyword}: {element.value}\n"
        else:
            tags_text += "No equipment information available.\n"
        self.tagsDisplay.setPlainText(tags_text)

    def view_private_information(self):
        """Display Private Information."""
        tags_text = "Private Information:\n" + "-" * 50 + "\n"
        if self.dicom_file:
            for element in self.dicom_file:
                if element.is_private and element.value:
                    tags_text += f"{element.tag}: {element.value}\n"
        else:
            tags_text += "No private information available.\n"
        self.tagsDisplay.setPlainText(tags_text)

    def view_other_information(self):
        """Display Other Information."""
        tags_text = "Other Information:\n" + "-" * 50 + "\n"
        if self.dicom_file:
            for element in self.dicom_file:
                if element.keyword not in [
                    "PixelData", "PatientName", "PatientID", "PatientBirthDate", "PatientSex",
                    "StudyInstanceUID", "StudyDate", "StudyTime", "ReferringPhysicianName", "AccessionNumber",
                    "SeriesInstanceUID", "SeriesNumber", "Modality", "InstanceNumber",
                    "ImagePositionPatient", "ImageOrientationPatient", "PixelSpacing", "SliceThickness",
                    "Manufacturer", "ManufacturerModelName", "SoftwareVersions", "DeviceSerialNumber",
                ] and element.value:
                    tags_text += f"{element.keyword}: {element.value}\n"
        else:
            tags_text += "No additional information available.\n"
        self.tagsDisplay.setPlainText(tags_text)

    def search_tag(self):
        search_term, ok = QInputDialog.getText(self, "Search Tag", "Enter tag keyword to search:")
        if ok and search_term:
            tags_text = self.tagsDisplay.toPlainText()
            matching_lines = [line for line in tags_text.split('\n') if search_term.lower() in line.lower()]
            if matching_lines:
                self.tagsDisplay.setPlainText("\n".join(matching_lines))
            else:
                self.tagsDisplay.setPlainText(f"No tags found matching '{search_term}'.")

    def anonymize_dicom(self):
        if self.dicom_file:  # Single file anonymization
            self.anonymize_single_file(self.dicom_file)

    def anonymize_single_file(self, dicom_data):
        prefix = self.prefixInput.text() or "Anon"
        try:
            for element in dicom_data:
                if element.keyword in ["PatientName", "PatientID", "AccessionNumber", "StudyInstanceUID"]:
                    dicom_data[element.tag].value = f"{prefix}_{np.random.randint(1000, 9999)}"
            filepath, _ = QFileDialog.getSaveFileName(self, "Save Anonymized DICOM File", "", "DICOM Files (*.dcm)")
            if filepath:
                dicom_data.save_as(filepath)
                self.tagsDisplay.setPlainText(f"DICOM file anonymized and saved to:\n{filepath}")
            else:
                self.tagsDisplay.setPlainText("File saving cancelled.")
        except Exception as e:
            self.tagsDisplay.setPlainText(f"Error anonymizing DICOM file: {e}")

stylesheet = """ 
QWidget{ background-color: rgb(30,30,30);color: White;}
QLabel{ color: White;}
QPushButton {color: White; }
QTabWidget  {color: White; }

    QTextEdit {

               /* Blue text (rgb(9, 132, 227)) */
        border: 1px solid rgb(9, 132, 227);    /* Gray border */
    }


    QTextEdit QScrollBar::up-arrow:vertical, 
    QTextEdit QScrollBar::down-arrow:vertical {
        background: rgb(9, 132, 227);   /* Arrow color */

    }


"""

if __name__ == "__main__":
    app = QApplication([])
    app.setStyle('Fusion')
    app.setStyleSheet(stylesheet)
    viewer = DicomViewer()
    viewer.show()
    app.exec()
