# ExamProct: AI-Powered Online Exam Proctoring System  

**ExamProct** is an advanced AI-driven online exam proctoring system designed to ensure the integrity of remote assessments. Using **deep learning, computer vision, and real-time monitoring**, it detects cheating behaviors and provides automated alerts to proctors.  

## ✨ Features  
- **Face Detection & Authentication** 🧑‍🎓  
  - Verifies the student's identity before and during the exam.  
  - Detects multiple faces to prevent impersonation.  

- **Gaze & Head Pose Tracking** 👀  
  - Monitors student focus to detect suspicious head movements.  
  - Identifies if the student looks away frequently or interacts with external resources.  

- **Object & Device Detection** 📱💻  
  - Recognizes unauthorized devices (phones, tablets, etc.) within the exam environment.  

- **Browser Activity Monitoring** 🌐  
  - Detects multiple tabs or switching between applications.  
  - Alerts proctors if the student attempts to search for answers.  

- **Automated Alerts & Reports** ⚠️📊  
  - Sends real-time alerts when suspicious behavior is detected.  
  - Generates detailed exam logs with timestamps and activity summaries.  

## 🚀 Technology Stack  
- **Deep Learning:** YOLO for face and object detection  
- **Computer Vision:** OpenCV for real-time video analysis  
- **Backend:** Flask/Django for API and server-side processing  
- **Frontend:** React.js for the user interface  
- **Database:** MongoDB/PostgreSQL for storing exam logs and reports  

## 🔧 Setup & Installation  
1. Clone the repository:  
   ```bash
   git clone https://github.com/yourusername/ExamProct.git  
   cd ExamProct  
   ```  
2. Create and activate a virtual environment:  
   ```bash
   python -m venv vir  
   vir\Scripts\activate  
   ```  
3. Install required packages:  
   ```bash
   pip install dlib-19.22.99-cp310-cp310-win_amd64.whl  
   pip install -r requirements.txt  
   ```  
4. Fix NumPy compatibility (optional):  
   ```bash
   pip uninstall numpy  
   pip install numpy==1.24.0  
   ```  
5. Start the server:  
   ```bash
   python manage.py runserver  
   ```

## 📌 Future Enhancements  
- **Voice Detection** to monitor for unauthorized conversations.  
- **AI-powered Behavior Analysis** for advanced cheating detection.  
- **Multi-language Support** for broader accessibility.  
