# YT Chat to Video - Comprehensive Documentation

A powerful tool to convert YouTube live chat streams into customizable video overlays, specifically designed for streamers and video editors who want to preserve chat history in their VODs or highlight reels.

---

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [GUI Guide](#gui-guide)
   - [Main Tab](#main-tab)
   - [Video Tab](#video-tab)
   - [Style Tab](#style-tab)
   - [Advanced Tab (EDL)](#advanced-tab-edl)
5. [CLI Usage](#cli-usage)
6. [The EDL Workflow](#the-edl-workflow)
7. [Role-based Styling](#role-based-styling)
8. [Troubleshooting](#troubleshooting)

---

## Overview

**YT Chat to Video** renders YouTube chat logs (JSON) into a transparent or opaque video file (MP4, MOV, WEBM) that can be imported into video editors like Premiere Pro, DaVinci Resolve, or Final Cut Pro. It supports:
- **Accuracy**: Calculates precise timing for messages relative to video start.
- **Customization**: extensive styling for different user roles (Owner, Moderator, Member, Normal).
- **EDL Support**: Automatically cuts the chat video to match your edited gameplay footage using Edit Decision Lists (.edl).
- **Formats**: Supports H.264, HEVC, ProRes 4444 (Transparent), and AV1.

---

## Installation

### Prerequisites
- **Python 3.10+**
- **FFmpeg**: Must be installed and accessible in your system PATH.
  - *MacOS*: `brew install ffmpeg`
  - *Windows*: Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and add `bin` folder to PATH.

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/8wapnil/yt-chat-to-video.git
   cd yt-chat-to-video
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Required packages:* `customtkinter`, `Pillow`, `requests`, `yt-dlp` (optional, for fetching JSON).

---

## Quick Start
1. **Run the GUI**:
   ```bash
   python3 gui.py
   ```
2. **Input**: Paste a YouTube Video URL (if chat replay is available) OR select a downloaded `.json` chat file.
3. **Output**: Choose a destination filename.
4. **Render**: Click "Render Video".

---

## GUI Guide

### Main Tab
- **YouTube URL**: Direct link to a VOD. The tool will attempt to download the live chat JSON.
- **Local JSON**: Use a pre-downloaded chat log (recommended for speed).
- **Output File**: Path to save the resulting video.

### Video Tab
- **Resolution**: Width x Height of the chat box (e.g., 400x1080).
- **Framerate**: Updates per second (default 60). Higher = smoother scrolling.
- **Codec**:
  - `H.264`: Standard, widely compatible. No transparency.
  - `HEVC`: High efficiency. Supports transparency on Apple devices.
  - `ProRes 4444`: Professional standard for transparency. Large file size.
  - `AV1`: Open, high efficiency.
- **Transparent Background**: Enables alpha channel (requires valid codec like ProRes/HEVC).
- **Background Color**: Visible if transparency is off.

### Style Tab
Customize the look of the chat.
- **Global Fonts**: Select `.ttf` files for Author Names and Message Text.
- **Role Settings**: Different styles for:
  - *Owner* (Broadcaster)
  - *Moderator* (Blue wrench)
  - *Member* (Subscribers)
  - *Normal* (Viewers)
- **Attributes per Role**:
  - Name Color, Message Color
  - Font Sizes (Name & Message)
  - Avatar Size, Emoji Size
  - Padding & Line Height

### Advanced Tab (EDL)
- **Use EDL**: Enable automated cutting.
- **EDL File**: Load a `.edl` file exported from your editor.
- **Clip Name**: The specific source clip name in your timeline that corresponds to the raw stream (e.g., "Stream Recording.mkv").
- **Analysis**: The tool parses the EDL to find every timestamp where "Stream Recording.mkv" appears and renders *only* those segments of chat, perfectly synchronized.

---

## CLI Usage

For power users or batch processing, use `yt-chat-to-video.py` directly.

```bash
python3 yt-chat-to-video.py [INPUT] [OPTIONS]
```

### Examples
**Basic Render:**
```bash
python3 yt-chat-to-video.py chat.json -o out.mp4
```

**Transparent ProRes:**
```bash
python3 yt-chat-to-video.py chat.json -o out.mov --codec prores --transparent
```

**With EDL:**
```bash
python3 yt-chat-to-video.py chat.json --edl timeline.edl --clip-name "Source.mp4" -o out.mov
```

### Key Arguments
| Flag | Description |
|------|-------------|
| `-o` | Output filename |
| `-w`, `-h` | Width/Height |
| `--codec` | h264, hevc, prores, av1 |
| `--transparent` | Enable alpha channel |
| `--color-owner` | Hex color for owner names |
| `--skip-avatars` | Don't download/render user pics |

---

## The EDL Workflow

This is the "killer feature" for editors. instead of rendering 4 hours of chat for a 10-minute highlight video:

1.  **Edit your video** in Premiere/Resolve. Cut up your VOD as much as you want. Time-remap (speed up) or re-order clips.
2.  **Export EDL**: File > Export > Timeline > EDL (CMX 3600).
3.  **Load in Tool**:
    - Select your full chat JSON.
    - Load the `.edl` file.
    - Select the **Clip Name** (the filename of your raw footage as seen in the editor).
4.  **Render**: The tool will generate a video that *only* contains chat for the parts of the stream you kept, with "gaps" automatically handled.
5.  **Import**: Drag the generated chat video into your timeline and align it with the start. It will match your cuts perfectly.

*Note: Dissolves and Wipes in EDL are treated as cuts.*

---

## Troubleshooting

- **"FFMPEG exited early"**: Usually means invalid arguments (e.g., odd resolution for specific codecs) or missing libraries. Check logs.
- **"Image data size mismatch"**: The rendered PIL image doesn't match the ffmpeg buffer. Ensure width/height are even numbers.
- **No Chat appearing**: Check the "Start/End Time" or EDL. If your video starts at 01:00:00 but you rendered from 00:00:00, it might be desynced.
- **Tkinter Errors**: Ensure you have Python with tcl/tk support (standard on most Windows/Mac installers). Linux users might need `sudo apt install python3-tk`.
