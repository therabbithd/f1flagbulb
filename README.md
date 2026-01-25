# F1 Flag Monitor & Smart Bulb Integration

A modern Python dashboard that monitors F1 Live Timing in real-time and Synchronizes a TP-Link Kasa smart bulb with the race track status (Yellow flags, Safety Car, Red Flag, etc.).

![F1 Dashboard](https://img.shields.io/badge/F1-Live_Timing-red?style=for-the-badge&logo=formula1)
![TPLink Kasa](https://img.shields.io/badge/Kasa-Smart_Home-00ADEF?style=for-the-badge&logo=tplink)

## 🏎️ Features

- **Real-time Monitoring**: Connects directly to F1's SignalR streaming service.
- **Smart Home Sync**: Automatically changes your Kasa bulb color based on track status:
    - 🟢 **Green**: All Clear
    - 🟡 **Yellow**: Yellow Flag / Caution
    - 🟠 **Orange**: Safety Car
    - 🔴 **Red**: Red Flag
    - 🟣 **Magenta**: Virtual Safety Car (VSC)
- **Modern GUI**: Built with `CustomTkinter` for a sleek, dark-themed dashboard.
- **Background Processing**: Monitoring loop runs in a background thread to keep the UI smooth.
- **Manual Control**: Test buttons in the UI to manually verify bulb colors.

## 🛠️ Prerequisites

- Python 3.8+
- A TP-Link Kasa/Tapo smart bulb (compatible with `python-kasa`).
- An active internet connection.

## 📦 Installation

1. **Clone or download** this repository.
2. **Install the required dependencies**:
   ```bash
   pip install customtkinter python-kasa python-dotenv requests websockets pillow
   ```

## ⚙️ Configuration

Create a `.env` file in the root directory and add your credentials:

```env
KASA_USERNAME=your_email@example.com
KASA_PASSWORD=your_secure_password
KASA_IP=192.168.1.XX
```

> [!TIP]
> You can find the IP address of your bulb using the Kasa/Tapo app or by running `kasa discover`.

## 🚀 Usage

Run the main application:
```bash
python main.py
```

- **F1 Live Timing**: The app will automatically wait for an active F1 session.
- **Manual Test**: Use the buttons at the bottom of the window to change the bulb color manually.

## 📁 Project Structure

- `main.py`: Main application (GUI, F1 Monitor, and Kasa control).
- `.env`: (Ignored) Sensitive credentials.
- `.gitignore`: Prevents uploading `.env` and temporary files to Git.

## 📜 Credits

- Inspired by F1 Live Timing SignalR protocol.
- Built using [python-kasa](https://github.com/python-kasa/python-kasa) and [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).
