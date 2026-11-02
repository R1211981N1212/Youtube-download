"""YT Downloader - Android app (Kivy + yt-dlp).

Only download videos you own, that are freely licensed, or that you have
permission to save.
"""
import os
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.utils import platform

try:
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
except Exception:
    pass


def out_dir(audio):
    if platform == "android":
        base = "/storage/emulated/0"
        sub = "Music" if audio else "Movies"
        path = os.path.join(base, sub, "YTDownloader")
    else:
        path = os.path.join(os.path.expanduser("~"), "Downloads")
    os.makedirs(path, exist_ok=True)
    return path


class Root(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", padding=16, spacing=12, **kw)
        Window.clearcolor = (0.07, 0.07, 0.07, 1)

        self.add_widget(Label(text="YT Downloader", font_size="24sp",
                              size_hint_y=None, height=60))
        self.url = TextInput(hint_text="Paste video link", multiline=False,
                             size_hint_y=None, height=56, font_size="16sp")
        self.add_widget(self.url)
        self.mode = Spinner(text="Video (MP4)",
                            values=("Video (MP4)", "Audio only (M4A)"),
                            size_hint_y=None, height=56)
        self.add_widget(self.mode)
        self.btn = Button(text="Download", size_hint_y=None, height=60,
                          background_color=(0.83, 0.18, 0.18, 1))
        self.btn.bind(on_release=self.start)
        self.add_widget(self.btn)
        self.bar = ProgressBar(max=100, value=0, size_hint_y=None, height=16)
        self.add_widget(self.bar)
        self.status = Label(text="Ready", halign="center", valign="top")
        self.status.bind(size=lambda w, s: setattr(w, "text_size", (s[0], None)))
        self.add_widget(self.status)

    def set_status(self, text, pct=None):
        def _u(dt):
            self.status.text = text
            if pct is not None:
                self.bar.value = pct
        Clock.schedule_once(_u)

    def start(self, *_):
        link = self.url.text.strip()
        if not link:
            self.set_status("Paste a link first")
            return
        self.btn.disabled = True
        self.set_status("Starting...", 0)
        threading.Thread(target=self.work, args=(link,), daemon=True).start()

    def work(self, link):
        try:
            import yt_dlp
            audio = self.mode.text.startswith("Audio")
            folder = out_dir(audio)

            def hook(d):
                if d["status"] == "downloading":
                    total = d.get("total_bytes") or d.get("total_bytes_estimate")
                    if total:
                        p = d["downloaded_bytes"] / total * 100
                        self.set_status("Downloading... %.1f%%" % p, p)
                elif d["status"] == "finished":
                    self.set_status("Finishing...")

            opts = {
                "outtmpl": os.path.join(folder, "%(title).80s.%(ext)s"),
                "progress_hooks": [hook],
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
                "restrictfilenames": True,
            }
            if audio:
                opts["format"] = "bestaudio[ext=m4a]/bestaudio"
            else:
                # single-file MP4 (no ffmpeg needed on the phone)
                opts["format"] = "b[ext=mp4]/best"
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([link])
            self.set_status("Done! Saved in:\n" + folder, 100)
        except Exception as e:
            self.set_status("Error: " + str(e)[:300])
        finally:
            Clock.schedule_once(lambda dt: setattr(self.btn, "disabled", False))


class YTApp(App):
    title = "YT Downloader"

    def build(self):
        if platform == "android":
            try:
                from android.permissions import request_permissions
                request_permissions([
                    "android.permission.READ_EXTERNAL_STORAGE",
                    "android.permission.WRITE_EXTERNAL_STORAGE",
                    "android.permission.READ_MEDIA_VIDEO",
                    "android.permission.READ_MEDIA_AUDIO",
                ])
            except Exception:
                pass
        return Root()


if __name__ == "__main__":
    YTApp().run()
