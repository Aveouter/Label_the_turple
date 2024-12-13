# Label_the_turple

**Triple Annotation：**cutting-edge solution designed to facilitate the precise labeling and management of triplet data structures essential for knowledge graph construction, natural language processing, and semantic analysis.

## Quick start

run the main_label.py to start the UI.

```python
python main_label.py
```

## Function

We built this application based on [Visual Genome Annotator](https://github.com/qqqqhhqq/visual-genome-annotator). This PyQt5-based image annotation tool offers the following key features:

### 1. Image Management
- **Load Images**: Supports bulk loading of images from a specified directory.
- **Navigate Images**: Easily switch between images using "Previous" and "Next" buttons.

### 2. Object Annotation
- **Create Annotations**: Users can label objects within images and draw corresponding shapes on the canvas.
- **Manage Labels**: Add, display, and delete object labels through a visual list interface.

### 3. Relationship Annotation
- **Define Relationships**: Establish relationships between annotated objects by selecting or entering predicates.
- **Manage Relationships**: Add, display, and delete relationship labels in a visual list.

### 4. Save and Load Annotations
- **Save Annotations**: Store object and relationship annotations in JSON files for persistent storage.
- **Load Annotations**: Retrieve and restore annotations from existing JSON files to continue editing.

### 5. User Interface
- **Intuitive Layout**: Utilizes vertical and grid layouts to organize widgets such as labels, lists, and buttons.
- **Scrollable Canvas**: Features a scrollable area to accommodate large images and detailed annotations.
- **Menu Bar and Status Bar**: Provides file operation options and real-time status updates to keep users informed.

### 6. Keyboard Shortcuts
- **Drawing Control**: Use the `Ctrl` key to toggle drawing modes, such as switching to square shapes.
- **Delete Operations**: Press the `Delete` key to remove selected relationship annotations efficiently.

### 7. Logging and Error Handling
- **Logging System**: Integrated logging for debugging and tracking errors, facilitating easier troubleshooting.
- **Error Messages**: Displays informative messages and warnings to users via message boxes for better user experience.

### 8. Virtual Environment Support (Optional)
- **Dependency Management**: Encourages the use of Python virtual environments to manage project dependencies, ensuring environment isolation and consistency.

### Workflow
1. **Launch Application**: Start the application using command-line arguments to specify image and annotation directories.
2. **Select Directory**: Use the "Open Folder" button to choose the directory containing images.
3. **Annotate Images**: Draw and label objects on the canvas, and define relationships between them.
4. **Save Annotations**: Regularly save annotation data to JSON files to ensure changes are preserved.
5. **Manage Annotations**: Browse, edit, or delete existing annotations to maintain data accuracy and completeness.

### Extensibility
The application is designed with modularity in mind, allowing for easy extension and customization. Developers can add new annotation types, integrate machine learning models for automatic annotation, or enhance the user interface to improve the overall user experience.

---