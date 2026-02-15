# Racing Flag Monitor & Smart Bulb Integration

A modern Python dashboard that monitors F1 and NASCAR Live Timing in real-time and synchronizes a TP-Link Kasa smart bulb with the race track status (Yellow flags, Safety Car, Red Flag, etc.).

![F1 Dashboard](https://img.shields.io/badge/F1-Live_Timing-red?style=for-the-badge&logo=formula1)
![NASCAR](https://img.shields.io/badge/NASCAR-Live_Feed-004B8D?style=for-the-badge)
![TPLink Kasa](https://img.shields.io/badge/Kasa-Smart_Home-00ADEF?style=for-the-badge&logo=tplink)

## 🏎️ Features

- **Multi-Series Support**: Switch between **F1** and **NASCAR** directly from the GUI.
- **Real-time Monitoring**:
    - **F1**: Connects directly to F1's SignalR streaming service.
    - **NASCAR**: Polls NASCAR's Live Feed API for instant updates.
- **Smart Home Sync**: Automatically changes your Kasa bulb color based on track status:
    - **F1 Flags**: 🟢 Green, 🟡 Yellow, 🟠 SC/VSC, 🔴 Red.
    - **NASCAR Flags**: 🟢 Green, 🟡 Caution, 🔴 Red, ⚪ White, 🏁 Checkered.
- **Modern GUI**: Built with `CustomTkinter` for a sleek, dark-themed dashboard with a built-in terminal log.
- **Manual Control**: Test buttons to manually verify bulb colors for each series.

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
> You can find the IP address of your bulb using the Kasa/Tapo app or by running `kasa discover`. You can also update the bulb IP directly in the GUI.

## 🚀 Usage

Run the main application:
```bash
python main.py
```

1. **Select Series**: Choose between F1 and NASCAR using the toggle at the top.
2. **Monitor**: The app will automatically connect and wait for live session updates.
3. **Manual Test**: Use the color buttons to test your bulb integration.

## 📁 Project Structure

- `main.py`: Entry point, coordinates monitors and GUI.
- `gui.py`: sleek `CustomTkinter` interface.
- `f1_monitor.py`: F1 SignalR client implementation.
- `nascar_monitor.py`: NASCAR API polling monitor.
- `kasa_manager.py`: Handles Kasa bulb discovery and color control.
- `config.py`: Centralized configuration and flag-to-color mappings.

## 📜 Credits

- Inspired by F1 Live Timing SignalR protocol.
- NASCAR live data via NASCAR.com Live Feed.
- Built using [python-kasa](https://github.com/python-kasa/python-kasa) and [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).
