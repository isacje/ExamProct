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
2. Install dependencies:  
   ```bash
   pip install -r requirements.txt  
   ```  
3. Start the server:  
   ```bash
   python app.py  
   ```  

## 📌 Future Enhancements  
- **Voice Detection** to monitor for unauthorized conversations.  
- **AI-powered Behavior Analysis** for advanced cheating detection.  
- **Multi-language Support** for broader accessibility.  

📢 **Contributions are welcome!** Feel free to fork, submit issues, and improve ExamProct. Let's make online exams more secure! 🚀
