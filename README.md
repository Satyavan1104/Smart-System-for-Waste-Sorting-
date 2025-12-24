#  Smart Waste Sorting System 

An AI-powered waste sorting system that efficiently classifies waste into categories such as **recyclable, compostable, non-recyclable, dry, and wet waste**. This system helps reduce contamination in recycling streams and increases material recovery rates.

##  Features

### **Main Page**
- Provides information about waste types, disposal methods, and environmental impact.
- Includes a **login/register** menu at the top right.

### **Authentication**
- **Login**: Redirects users to the waste detection dashboard.
- **Register**: Allows new users to create an account.

### **User Dashboard**
- **Waste Detection by Uploading Images** 
  - Users can upload images of waste to be classified by the AI model.
- **Real-Time Waste Detection** 
  - Live waste classification using the camera.
- **Add Waste Location** 
  - Users can mark waste locations on a map with latitude and longitude.
- **View Location History** 
  - Users can track previously reported waste locations and their statuses.

### **Admin Dashboard**
- **Manage Waste Reports** 
  - View location details, usernames, latitude, and longitude.
  - Change the status of waste reports to **"Completed"**, which updates the user's history.
- **View Waste Locations on a Map** 
  - Interactive map showing all reported waste locations.

## **Technology Used**
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask (Python)
- **Machine Learning**: TensorFlow, OpenCV, CNN, YOLO/SSD for object detection
- **Database**: MySQL (for user data and waste location tracking)
