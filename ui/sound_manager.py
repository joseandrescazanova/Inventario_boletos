"""
MANEJADOR DE SONIDOS PARA LA APLICACIÓN
"""

import os
import platform
from enum import Enum
from typing import Optional

try:
    import pygame

    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class TipoSonido(Enum):
    """Tipos de sonidos disponibles"""

    EXITO = "exito"
    ADVERTENCIA = "advertencia"
    ERROR = "error"


class SoundManager:
    """Manejador de sonidos para la aplicación"""

    def __init__(self, sounds_dir: str = None):
        """
        Inicializa el manejador de sonidos.

        Args:
            sounds_dir: Directorio donde están los archivos de sonido
        """
        # Usar ruta relativa desde el directorio del proyecto
        if sounds_dir is None:
            # Directorio base del proyecto
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # Ir a assets/sounds
            sounds_dir = os.path.join(project_dir, "assets", "sounds")

        self.sounds_dir = sounds_dir
        self.sounds_loaded = False
        self.use_pygame = PYGAME_AVAILABLE
        self.sounds = {}

        # Verificar si el directorio existe
        if not os.path.exists(self.sounds_dir):
            print(
                f"Advertencia: Directorio de sonidos no encontrado: {self.sounds_dir}"
            )
            print(f"Directorio actual de trabajo: {os.getcwd()}")
            return

        # Cargar sonidos si pygame está disponible
        if self.use_pygame:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self._load_sounds()
                self.sounds_loaded = True
                print(f"SoundManager inicializado: {len(self.sounds)} sonidos cargados")
            except Exception as e:
                print(f"Error inicializando pygame mixer: {e}")
                self.use_pygame = False
                print("Usando métodos alternativos para sonidos")

    def _load_sounds(self):
        """Carga todos los archivos de sonido"""
        if not PYGAME_AVAILABLE or not os.path.exists(self.sounds_dir):
            return

        # Mapeo de tipos de sonido a archivos
        sound_files = {
            TipoSonido.EXITO: "exito.mp3",
            TipoSonido.ADVERTENCIA: "advertencia.mp3",
            TipoSonido.ERROR: "error.mp3",
        }

        for tipo, filename in sound_files.items():
            filepath = os.path.join(self.sounds_dir, filename)
            if os.path.exists(filepath):
                try:
                    self.sounds[tipo] = pygame.mixer.Sound(filepath)
                    print(f"✓ Sonido cargado: {filename}")
                except Exception as e:
                    print(f"✗ Error cargando sonido {filename}: {e}")
            else:
                print(f"⚠ Archivo de sonido no encontrado: {filepath}")

    def play(self, tipo_sonido: TipoSonido):
        """
        Reproduce un sonido según el tipo.

        Args:
            tipo_sonido: Tipo de sonido a reproducir
        """
        # Intentar con pygame primero
        if self.use_pygame and self.sounds_loaded and tipo_sonido in self.sounds:
            try:
                self.sounds[tipo_sonido].play()
                return True
            except Exception as e:
                print(f"Error reproduciendo sonido con pygame: {e}")
                self.use_pygame = False

        # Fallback a sonidos del sistema
        return self._play_fallback(tipo_sonido)

    def _play_fallback(self, tipo_sonido: TipoSonido) -> bool:
        """Reproduce sonidos usando métodos alternativos"""
        sistema = platform.system()

        try:
            if sistema == "Linux":
                # Para Linux: usar paplay, aplay, o beep
                return self._play_linux(tipo_sonido)
            elif sistema == "Windows":
                # Para Windows: usar winsound
                return self._play_windows(tipo_sonido)
            elif sistema == "Darwin":  # macOS
                # Para macOS: usar afplay
                return self._play_macos(tipo_sonido)
            else:
                # Sistema no reconocido - usar beep simple
                return self._play_beep(tipo_sonido)
        except Exception as e:
            print(f"Error en fallback de sonido: {e}")
            return False

    def _play_linux(self, tipo_sonido: TipoSonido) -> bool:
        """Reproduce sonidos en Linux (Ubuntu/Debian)"""
        import subprocess

        # Obtener ruta del archivo de sonido
        filepath = self._get_sound_filepath(tipo_sonido)

        if filepath and os.path.exists(filepath):
            # Intentar varios reproductores en orden de preferencia
            reproductores = ["paplay", "aplay", "mpg123", "mpg321"]

            for reproductor in reproductores:
                try:
                    # Verificar si el reproductor está instalado
                    subprocess.run(
                        ["which", reproductor], capture_output=True, check=True
                    )
                    # Reproducir el sonido
                    subprocess.Popen(
                        [reproductor, filepath],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue

        # Fallback a beeps del terminal
        return self._play_beep(tipo_sonido)

    def _play_windows(self, tipo_sonido: TipoSonido) -> bool:
        """Reproduce sonidos en Windows"""
        try:
            import winsound

            # Primero intentar con archivo de sonido
            filepath = self._get_sound_filepath(tipo_sonido)
            if filepath and os.path.exists(filepath):
                try:
                    winsound.PlaySound(
                        filepath, winsound.SND_FILENAME | winsound.SND_ASYNC
                    )
                    return True
                except:
                    pass

            # Fallback a beeps del sistema
            sonidos = {
                TipoSonido.EXITO: (1000, 200),  # Beep alto y corto
                TipoSonido.ADVERTENCIA: (800, 300),  # Beep medio
                TipoSonido.ERROR: (400, 500),  # Beep bajo y largo
            }

            if tipo_sonido in sonidos:
                frecuencia, duracion = sonidos[tipo_sonido]
                winsound.Beep(frecuencia, duracion)
                return True

        except ImportError:
            print("winsound no disponible en este sistema")

        return False

    def _play_macos(self, tipo_sonido: TipoSonido) -> bool:
        """Reproduce sonidos en macOS"""
        import subprocess

        filepath = self._get_sound_filepath(tipo_sonido)
        if filepath and os.path.exists(filepath):
            try:
                subprocess.Popen(
                    ["afplay", filepath],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return True
            except:
                pass

        # Fallback a beep del sistema
        print("\a", end="", flush=True)
        return True

    def _play_beep(self, tipo_sonido: TipoSonido) -> bool:
        """Reproduce beeps básicos del terminal"""
        try:
            if tipo_sonido == TipoSonido.EXITO:
                # Beep corto y agradable
                print("\a", end="", flush=True)
            elif tipo_sonido == TipoSonido.ADVERTENCIA:
                # Dos beeps cortos
                for _ in range(2):
                    print("\a", end="", flush=True)
            elif tipo_sonido == TipoSonido.ERROR:
                # Tres beeps largos
                for _ in range(3):
                    print("\a", end="", flush=True)
                    import time

                    time.sleep(0.1)
            return True
        except:
            return False

    def _get_sound_filepath(self, tipo_sonido: TipoSonido) -> Optional[str]:
        """Obtiene la ruta del archivo de sonido para un tipo"""
        if not self.sounds_dir or not os.path.exists(self.sounds_dir):
            return None

        archivos = {
            TipoSonido.EXITO: "exito.mp3",
            TipoSonido.ADVERTENCIA: "advertencia.mp3",
            TipoSonido.ERROR: "error.mp3",
        }

        if tipo_sonido in archivos:
            filepath = os.path.join(self.sounds_dir, archivos[tipo_sonido])
            if os.path.exists(filepath):
                return filepath
            else:
                print(f"Archivo no encontrado: {filepath}")

        return None

    def get_sounds_status(self) -> dict:
        """Obtiene el estado de los sonidos cargados"""
        return {
            "pygame_available": PYGAME_AVAILABLE,
            "use_pygame": self.use_pygame,
            "sounds_loaded": self.sounds_loaded,
            "sounds_dir": self.sounds_dir,
            "sounds_available": list(self.sounds.keys()),
            "directory_exists": os.path.exists(self.sounds_dir)
            if self.sounds_dir
            else False,
        }
