1. Install Docker
2. Confirm installation: `docker run hello-world` - update user permissions as needed
3. Run `docker compose up --build -d` to start the application
4. The backend is now running at `localhost:5000`
5. To view/tail logs, run `docker compose logs -f`. To view logs for a specific service, run `docker compose logs -f <service_name>`
5. Saving files will automatically reload the server
6. Run `docker compose down` to stop the application
7. If you need to change packages available in the backend, update the `requirements.txt` file and rebuild the image (down then up)
8. Postgres setup and Troubleshooting
9. Run `docker ps` to check if your containers are up and running - you should see **tct_database** running. If not, try running `docker compose up -d`
10. Make sure you POSTGRES_PASSWORD and POSTGRES_USER are correctly configured in `.env` file or Docker Compose file
11. Run `psql -U postgres -h localhost -d tct_database`
12. Run `flask db upgrade` and make sure it completes without errors


### **README: Running an Expo + Flask Backend with Docker for the First Time**

## **Introduction**

This project demonstrates how to run an **Expo React Native frontend** and a **Flask backend** together in a Dockerized environment. It uses:
- **Flask** for the backend.
- **PostgreSQL** as the database.
- **Expo** for the frontend, which supports React Native development for iOS, Android, and Web.

---

## **Prerequisites**

Before running the project, ensure you have the following installed:

1. **Docker Desktop**:
   - Download and install from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop).
2. **Node.js and npm**:
   - Download and install from [https://nodejs.org/](https://nodejs.org/).
3. **Expo CLI** (optional for local testing):
   ```bash
   npm install -g expo-cli
   ```

---

## **Project Structure**

The project structure looks like this:

```
.
├── mobile/                       # Expo frontend
│   ├── .expo/                    # Expo-specific configuration (auto-generated)
│   ├── app/                      # Main application entry
│   ├── assets/                   # Static assets (e.g., images, fonts)
│   ├── components/               # Reusable UI components
│   ├── constants/                # Project constants (e.g., colors, styles)
│   ├── hooks/                    # Custom React hooks
│   ├── node_modules/             # Installed dependencies (auto-generated)
│   ├── scripts/                  # Utility scripts for project setup or deployment
│   ├── App.js                    # Main Expo app entry point
│   ├── app.json                  # Expo project configuration
│   ├── Dockerfile                # Dockerfile for building the Expo app
│   ├── package.json              # Project dependencies and scripts
│   └── ...                       # Other Expo files
├── app.py                        # Main Flask app
├── docker-compose.yml            # Docker configuration
└── README.md                     # Documentation for the project
```

---

## **Setup Instructions**

### **1. Build the Docker Images**
Use Docker Compose to build the project images:
```bash
docker compose build
```

---

### **3. Start the Containers**
Start the backend, database, and Expo frontend containers:
```bash
docker compose up
```

This will:
- Start the **Flask backend** on port `5001`.
- Start **PostgreSQL** on port `5432`.
- Start the **Expo frontend** with Metro Bundler on `8081`.

---

## **Running the Application**

### **1. Frontend (Expo)**
The Expo app will start on port `8081`. Open the Metro Bundler interface in your browser:
```
http://localhost:8081
```

#### **Options: [HAVING TROUBLE WITH THIS RIGHT NOW DO NOT DO THIS]** 
- **Run on iOS Simulator:** Press `i` in the terminal or click the option in Metro Bundler.
- **Run on Android Emulator:** Press `a` in the terminal or click the option in Metro Bundler.
- **Scan QR Code:** Open the **Expo Go** app on your mobile device and scan the QR code from Metro Bundler.


#### **FIRST TIME EXPO**
### **Using the Simulator for the First Time with Expo**

If this is your first time using Expo with a simulator, follow this guide to set up and run the app on an iOS simulator or Android emulator.

---

## **1. Prerequisites for Simulators**

### **iOS Simulator (Mac Only)**
1. **Install Xcode**:
   - Open the Mac App Store and download **Xcode**.
   - After installation, open Xcode and agree to the license terms.
2. **Install Xcode Command Line Tools**:
   ```bash
   xcode-select --install
   ```
3. **Verify Simulator Availability**:
   - Open Xcode > Preferences > Components.
   - Download any additional simulators (e.g., iOS 16.4).

---

### **Android Emulator**
1. **Install Android Studio**:
   - Download and install **Android Studio** from [https://developer.android.com/studio](https://developer.android.com/studio).
   - During installation, select the option to install the Android Virtual Device (AVD) Manager.
2. **Set Up an Android Emulator**:
   - Open **Android Studio**.
   - Go to **Tools > AVD Manager** and click **Create Virtual Device**.
   - Select a device (e.g., Pixel 4) and a system image (e.g., Android 13).
   - Finish setup and start the emulator.
3. **Verify Emulator Setup**:
   - Start the emulator and ensure it runs smoothly.

---

## **2. Running the Expo App on a Simulator**

### **Step 1: Start the Expo Project**
Ensure the Expo project is running:
```bash
docker compose up expo-frontend
```

**Simple Solution is to, alternatively, if running locally:**
```bash
cd mobile
npx expo start
```

Open the Metro Bundler interface in your browser or expo using following links through docker:
```
http://localhost:8081
exp://localhost:8081
```
![alt text](./expo_url.png)
---

### **Step 2: Open on iOS Simulator**
1. Ensure the iOS simulator is running. Open it manually via Xcode:
   - Xcode > Open Developer Tools > Simulator.
2. In the terminal running Expo, press:
   ```plaintext
   i
   ```
   - Expo CLI will automatically build and launch the app in the iOS simulator.

---

### **Step 3: Open on Android Emulator**
1. Start the Android emulator from Android Studio:
   - Open Android Studio > Tools > AVD Manager > Start Emulator.
2. In the terminal running Expo, press:
   ```plaintext
   a
   ```
   - Expo CLI will install the app and launch it in the Android emulator.

---

## **3. Troubleshooting Simulator Issues**

### **iOS Simulator Issues**
- **Simulator Not Opening Automatically**:
  - Open the simulator manually via Xcode:
    ```plaintext
    Xcode > Open Developer Tools > Simulator
    ```
  - Then press `i` in the terminal.
- **No Device Found**:
  - Ensure Xcode command-line tools are installed:
    ```bash
    xcode-select --install
    ```

---

### **Android Emulator Issues**
- **"No Connected Devices"**:
  - Verify that the emulator is running:
    ```bash
    adb devices
    ```
  - If no devices are listed, restart the emulator via Android Studio.
- **Expo CLI Can't Find Emulator**:
  - Ensure the `ANDROID_HOME` environment variable is set:
    ```bash
    export ANDROID_HOME=~/Library/Android/sdk
    export PATH=$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/tools:$ANDROID_HOME/tools/bin:$ANDROID_HOME/platform-tools
    ```
    Add these lines to your shell config (e.g., `.bashrc`, `.zshrc`).

---

### **4. Testing the App on the Simulator**
Once the app launches on the simulator:
- **Verify Backend Connectivity**:
  - The app should call the `/check-database` endpoint and display the response.
- **Reload the App**:
  - Press `cmd + d` (iOS) or `cmd + m` (Android) to open the developer menu.
  - Select **Reload**.

---





### **2. Backend (Flask)**
The Flask backend will start on port `5001`. Test the backend by accessing the `/check-database` endpoint:
```
http://localhost:5001/check-database
```

---



## **Accessing the Application**

### **Expo Frontend**
- **Web:** Visit `http://localhost:8081`.
- **Mobile Devices:** Use the Expo Go app and enter URL `exp://localhost:8081`.

### **Flask Backend**
Access the Flask backend via:
- Example endpoint: `http://localhost:5001/check-database`

---

## **Testing Backend Connection**

To verify the backend and frontend connection, follow these steps:

1. Start the app on a simulator or physical device.
2. The frontend should call the `/check-database` endpoint to verify backend connectivity.
3. The database status (e.g., "Database exists and is accessible") will display in the app.

---

## **Common Issues and Debugging**

### **1. Backend Not Accessible**
- Ensure the backend container is running:
  ```bash
  docker ps
  ```
- Check the logs for errors:
  ```bash
  docker logs flask-app
  ```

### **2. Expo Frontend Not Working**
- If the QR code doesn’t show, ensure Expo is started in tunnel mode:
  ```bash
  npx expo start --tunnel
  ```

---
