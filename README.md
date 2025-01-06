# **PROJECT RAPTOR**

---

## 🚀 **Overview**

**PROJECT RAPTOR** is a cutting-edge simulation of a stock exchange platform, built to demonstrate the fundamentals of networking protocols like **TCP** and **IP**. This project bridges the gap between theoretical concepts and real-world applications of networking while replicating stock market operations.

---

## 🔑 **Key Features**

### 🗄️ **Database Integration**
Powered by **Firebase**, the platform securely stores:
- 📊 **Stock Details**
- 👤 **Customer Data**
- 💳 **Banking Information**

### 🌐 **Networking Backbone**
- Built with **TCP/IP** for seamless communication between components.

### 💻 **Desktop Platform**
- **User Interface**: Designed with **PyQT** for a sleek and interactive experience.
- For enhanced performance, future iterations may utilize **Java**.

---

## 🎯 **Project Goals**

The primary objective of **PROJECT RAPTOR** is to offer a hands-on understanding of base networking protocols that form the backbone of modern systems, with a practical simulation of a stock exchange environment.

---

## 📋 **Prerequisites**

### 🔧 **Software Requirements**
- Python installed with:
  - **PyQT**
  - Firebase libraries

### 💻 **Compatible Platforms**
- **Windows**
- **Linux**

---

## ⚙️ **Setup Instructions**

### **Step 1: Configure IP Addresses**
1. Locate your **IPv4 address**:
   - **Windows**: Open Command Prompt and run:
     ```bash
     ipconfig
     ```
   - **Linux**: Open Terminal and run:
     ```bash
     ifconfig
     ```

### **Step 2: Running the Application**
1. Launch the following components **simultaneously** on the same network or separate terminals:

   **Banking Server**:
   ```bash
   python bankingserver.py
   ```

   **Main Server**:
   ```bash
   python server.py
   ```

   **Client Application**:
   ```bash
   python client.py
   ```

---

## 🖼️ **Screenshots**

### Login Page:
<img src="assets/login_page.png" alt="Login Page" width="500">

### Main Page:
<img src="assets/main_page.png" alt="Main Page" width="500">

### Portfolio Page:
<img src="assets/portfolio.png" alt="Portfolio Page" width="500">

---

## 📌 **Important Notes**

- Ensure all three components are running on devices connected to the **same network**.
- Verify IP addresses configured in the code.
- For better performance, consider optimizing the UI with **JavaFX** or **Swing**.

---

## 🛠️ **Troubleshooting**

### Common Issues & Solutions

1. **Connection Errors**
   - Confirm devices are on the **same network**.
   - Validate **IPv4 addresses** are configured correctly.

2. **Firebase Authentication Issues**
   - Ensure Firebase credentials are accurate.
   - Verify **internet connectivity**.
   - Provide the appropriate JSON file for authentication (refer to the code for database structure).

---

## 🌟 **Future Enhancements**

- Transition to a faster UI framework like **JavaFX** or **Swing**.
- Implement **SSL/TLS** for secure communication.
- Strengthen database security with advanced encryption methods.

---

**PROJECT RAPTOR**: Connecting concepts to real-world applications, one protocol at a time! 🌐

