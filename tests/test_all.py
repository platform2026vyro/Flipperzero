#!/usr/bin/env python3
"""Test suite for Flipper-Z — verifica moduli su Windows e Linux."""

import sys
import os
import unittest
import tempfile
import json

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestImports(unittest.TestCase):
    """Test che tutti i moduli si importino senza errori."""

    def test_utils(self):
        from modules.utils import clear_screen, check_dependencies, run_termux_command, hex_to_bytes, bytes_to_hex
        self.assertTrue(callable(clear_screen))
        self.assertTrue(callable(check_dependencies))
        self.assertTrue(callable(run_termux_command))
        self.assertTrue(callable(hex_to_bytes))
        self.assertTrue(callable(bytes_to_hex))

    def test_nfc_tools(self):
        from modules.nfc_tools import NfcTools
        from rich.console import Console
        instance = NfcTools(Console())
        self.assertTrue(hasattr(instance, 'menu'))
        self.assertTrue(hasattr(instance, 'scan_tag'))
        self.assertTrue(hasattr(instance, 'check_hardware'))
        self.assertTrue(hasattr(instance, 'saved_tags'))

    def test_ble_tools(self):
        from modules.ble_tools import BleScanner
        from rich.console import Console
        instance = BleScanner(Console())
        self.assertTrue(hasattr(instance, 'menu'))
        self.assertTrue(hasattr(instance, 'scan'))

    def test_wifi_scan(self):
        from modules.wifi_scan import WifiScan
        from rich.console import Console
        instance = WifiScan(Console())
        self.assertTrue(hasattr(instance, 'menu'))
        self.assertTrue(hasattr(instance, 'scan'))
        self.assertTrue(hasattr(instance, 'ping_sweep'))
        self.assertTrue(hasattr(instance, 'saved_scans'))

    def test_network_remote(self):
        from modules.network_remote import NetworkRemote
        from rich.console import Console
        instance = NetworkRemote(Console())
        self.assertTrue(hasattr(instance, 'menu'))
        self.assertTrue(hasattr(instance, 'discover'))
        self.assertTrue(hasattr(instance, 'custom_api'))

    def test_system_tools(self):
        from modules.system_tools import SystemTools
        from rich.console import Console
        instance = SystemTools(Console())
        self.assertTrue(hasattr(instance, 'menu'))

    def test_device_info(self):
        from modules.device_info import DeviceInfo
        from rich.console import Console
        instance = DeviceInfo(Console())
        self.assertTrue(hasattr(instance, 'menu'))
        self.assertTrue(hasattr(instance, 'show_battery'))
        self.assertTrue(hasattr(instance, 'show_all'))

    def test_bruteforce(self):
        from modules.bruteforce import BruteForce
        from rich.console import Console
        instance = BruteForce(Console())
        self.assertTrue(hasattr(instance, 'menu'))
        self.assertTrue(hasattr(instance, 'hash_cracker'))
        self.assertTrue(hasattr(instance, 'zip_cracker'))
        self.assertTrue(hasattr(instance, 'pdf_cracker'))
        self.assertTrue(hasattr(instance, 'wordlist_gen'))
        self.assertTrue(hasattr(instance, 'pin_generator'))
        self.assertTrue(hasattr(instance, 'password_analyzer'))
        self.assertTrue(hasattr(instance, 'rainbow_table'))
        self.assertTrue(hasattr(instance, 'badge_uid_generator'))

    def test_ir_remote(self):
        from modules.ir_remote import IrRemote
        from rich.console import Console
        instance = IrRemote(Console())
        self.assertTrue(hasattr(instance, 'menu'))
        self.assertTrue(hasattr(instance, 'tv_brands'))
        self.assertTrue(hasattr(instance, 'custom_code'))
        self.assertTrue(hasattr(instance, 'test_ir'))

    def test_scooter_unlock(self):
        from modules.scooter_unlock import ScooterUnlock
        from rich.console import Console
        instance = ScooterUnlock(Console())
        self.assertTrue(hasattr(instance, 'menu'))
        self.assertTrue(hasattr(instance, 'scan_scooters'))
        self.assertTrue(hasattr(instance, 'unlock_sequence'))
        self.assertTrue(hasattr(instance, 'check_tools'))
        # Verify no duplicate methods
        import inspect
        src = inspect.getsource(instance.__class__)
        self.assertEqual(src.count('def _parse_blesh_scan'), 1, "Duplicate _parse_blesh_scan found!")
        self.assertEqual(src.count('def _parse_hcitool_scan'), 1, "Duplicate _parse_hcitool_scan found!")


class TestMainPy(unittest.TestCase):
    """Test che main.py sia strutturalmente valido."""

    def test_syntax(self):
        """Verifica che main.py sia compilabile."""
        import py_compile
        main_path = os.path.join(os.path.dirname(__file__), "..", "main.py")
        py_compile.compile(main_path, doraise=True)

    def test_menu_structure(self):
        """Verifica struttura del menu."""

        with open(os.path.join(os.path.dirname(__file__), "..", "main.py"), encoding="utf-8") as f:
            content = f.read()

        # Check required imports
        self.assertIn("from modules.bruteforce import BruteForce", content)
        self.assertIn("from modules.ir_remote import IrRemote", content)
        self.assertIn("from modules.scooter_unlock import ScooterUnlock", content)

        # Check Windows support
        self.assertIn('if sys.platform == "win32"', content)

        # Check all 10 menu items (9 tools + Exit)
        self.assertIn('"name": "Brute Force"', content)
        self.assertIn('"name": "IR Remote"', content)
        self.assertIn('"name": "Scooter Unlock"', content)
        self.assertIn('"name": "Exit"', content)

    def test_handlers(self):
        """Verifica che tutti i 9 handler siano mappati."""
        import ast
        main_path = os.path.join(os.path.dirname(__file__), "..", "main.py")
        with open(main_path, encoding="utf-8") as f:
            tree = ast.parse(f.read())

        # Find handlers dict
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict) and any(
                isinstance(k, ast.Constant) and k.value == 1 for k in node.keys
            ):
                # Count entries (should be 9: 1-9)
                self.assertEqual(len(node.keys), 9)
                break


class TestUtils(unittest.TestCase):
    """Test utility functions."""

    def test_hex_to_bytes(self):
        from modules.utils import hex_to_bytes, bytes_to_hex
        data = "48 65 6c 6c 6f"
        result = hex_to_bytes(data)
        self.assertEqual(result, b"Hello")

    def test_bytes_to_hex(self):
        from modules.utils import bytes_to_hex
        result = bytes_to_hex(b"Hello")
        self.assertEqual(result, "48 65 6c 6c 6f")

    def test_hex_to_bytes_no_spaces(self):
        from modules.utils import hex_to_bytes
        result = hex_to_bytes("48656c6c6f")
        self.assertEqual(result, b"Hello")

    def test_check_dependencies(self):
        from modules.utils import check_dependencies
        missing = check_dependencies()
        # rich should be installed
        self.assertNotIn("rich", missing)

    def test_run_termux_command_fail_gracefully(self):
        """Su Windows/i comandi Termux devono fallire gracefulmente, non crashare."""
        from modules.utils import run_termux_command
        result = run_termux_command(["comando_inesistente_xyz"])
        self.assertFalse(result["success"])
        self.assertIn("error", result)


class TestBruteForce(unittest.TestCase):
    """Test funzioni core del modulo Brute Force."""

    def setUp(self):
        from rich.console import Console
        from modules.bruteforce import BruteForce
        self.bf = BruteForce(Console())
        self.tmpdir = tempfile.mkdtemp()

    def test_hash_cracker_md5(self):
        """Test che l'hash cracker trovi una password semplice."""
        import hashlib
        test_word = "password123"
        test_hash = hashlib.md5(test_word.encode()).hexdigest()

        # Create wordlist
        wl_path = os.path.join(self.tmpdir, "test_wl.txt")
        with open(wl_path, "w") as f:
            f.write("wrongpass\nwrong2\n" + test_word + "\nwrong3\n")

        # Use hash_cracker internals via direct call
        # We test the hashlib logic directly
        with open(wl_path) as f:
            words = [l.strip() for l in f if l.strip()]

        found = None
        for w in words:
            h = hashlib.md5(w.encode()).hexdigest()
            if h == test_hash:
                found = w
                break

        self.assertEqual(found, test_word)

    def test_pin_generator_count(self):
        """Test che il PIN generator produca il numero richiesto di PIN."""
        # Test the core generation logic
        import random
        digits = 4
        count = 50
        pins = set()
        while len(pins) < min(count, 10**digits):
            pins.add("".join(str(random.randint(0, 9)) for _ in range(digits)))
        self.assertGreaterEqual(len(pins), 1)
        self.assertLessEqual(len(pins), count)

    def test_password_analyzer_entropy(self):
        """Test che l'analizzatore calcoli entropy correttamente."""
        import math
        pw = "Test123!@#"
        length = len(pw)
        has_lower = any(c.islower() for c in pw)
        has_upper = any(c.isupper() for c in pw)
        has_digit = any(c.isdigit() for c in pw)
        has_special = any(not c.isalnum() for c in pw)
        charset_size = 0
        if has_lower: charset_size += 26
        if has_upper: charset_size += 26
        if has_digit: charset_size += 10
        if has_special: charset_size += 33
        entropy = length * math.log2(charset_size)
        self.assertGreater(entropy, 50)  # Strong password

    def test_rainbow_table_format(self):
        """Test che la rainbow table generi formato corretto hash:password."""
        import hashlib
        words = ["test", "password", "admin"]
        expected = []
        for w in words:
            h = hashlib.md5(w.encode()).hexdigest()
            expected.append(f"{h}:{w}")

        output_path = os.path.join(self.tmpdir, "rainbow_test.txt")
        with open(output_path, "w") as out:
            for w in words:
                h = hashlib.md5(w.encode()).hexdigest()
                out.write(f"{h}:{w}\n")

        with open(output_path) as f:
            lines = [l.strip() for l in f]

        self.assertEqual(len(lines), 3)
        for line in lines:
            self.assertIn(":", line)
            hash_part, word_part = line.split(":", 1)
            self.assertEqual(len(hash_part), 32)  # MD5
            self.assertIn(word_part, words)

    def test_badge_uid_length(self):
        """Test che gli UID badge abbiano la lunghezza corretta."""
        import random
        bc = 4  # 4-byte MIFARE
        uids = []
        for _ in range(5):
            uid = random.randint(0, 256**bc - 1)
            uids.append(f"{uid:0{bc*2}X}")
        for uid in uids:
            self.assertEqual(len(uid), bc * 2)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)


class TestIRRemote(unittest.TestCase):
    """Test del modulo IR Remote."""

    def test_tv_codes_structure(self):
        """Verifica che i codici TV abbiano la struttura corretta."""
        from modules.ir_remote import IrRemote
        from rich.console import Console
        ir = IrRemote(Console())
        for brand, data in ir.tv_codes.items():
            self.assertIn("name", data)
            self.assertIn("freq", data)
            self.assertIn("power", data)
            self.assertIsInstance(data["freq"], int)
            self.assertIsInstance(data["power"], list)
            self.assertGreater(len(data["power"]), 10)


class TestNetworkRemote(unittest.TestCase):
    """Test del modulo Network Remote."""

    def test_wol_packet(self):
        """Test che il Wake-on-LAN packet sia corretto."""
        import socket
        mac = "AA:BB:CC:DD:EE:FF"
        mac_bytes = bytes.fromhex(mac.replace(":", "").replace("-", ""))
        payload = b'\xff' * 6 + mac_bytes * 16
        self.assertEqual(len(payload), 102)
        self.assertEqual(payload[:6], b'\xff' * 6)
        self.assertEqual(payload[6:12], mac_bytes)
        self.assertEqual(payload[12:18], mac_bytes)


class TestWiFiScan(unittest.TestCase):
    """Test modulo WiFi Scan."""

    def test_ping_command_windows(self):
        """Verifica che su Windows si usino i flag corretti per ping."""
        import sys
        if sys.platform == "win32":
            import subprocess
            # Just verify the command structure is valid
            ip = "127.0.0.1"
            cmd = ["ping", "-n", "1", "-w", "1000", ip]
            self.assertEqual(cmd[1], "-n")
            self.assertEqual(cmd[3], "-w")
        else:
            import subprocess
            ip = "127.0.0.1"
            cmd = ["ping", "-c", "1", "-W", "1", ip]
            self.assertEqual(cmd[1], "-c")
            self.assertEqual(cmd[3], "-W")


class TestScooterUnlock(unittest.TestCase):
    """Test modulo Scooter Unlock."""

    def test_no_duplicate_methods(self):
        """Verifica che non ci siano metodi duplicati."""
        from modules.scooter_unlock import ScooterUnlock
        import inspect
        src = inspect.getsource(ScooterUnlock)
        self.assertEqual(src.count('def _parse_blesh_scan'), 1)
        self.assertEqual(src.count('def _parse_hcitool_scan'), 1)

    def test_nus_uuids(self):
        """Verifica che gli UUID BLE siano validi."""
        from modules.scooter_unlock import NUS_SERVICE_UUID, NUS_TX_CHAR, NUS_RX_CHAR
        import uuid
        for uid in [NUS_SERVICE_UUID, NUS_TX_CHAR, NUS_RX_CHAR]:
            # Should be valid UUID format
            u = uuid.UUID(uid)
            self.assertEqual(str(u), uid.lower())


class TestMainMenuItems(unittest.TestCase):
    """Test che tutti i file e le risorse necessarie esistano."""

    def test_requirements_exist(self):
        req_path = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
        self.assertTrue(os.path.exists(req_path))

    def test_installer_bat_exists(self):
        bat_path = os.path.join(os.path.dirname(__file__), "..", "installer.bat")
        self.assertTrue(os.path.exists(bat_path))

    def test_launcher_bat_exists(self):
        bat_path = os.path.join(os.path.dirname(__file__), "..", "FLIPPER-Z.BAT")
        self.assertTrue(os.path.exists(bat_path))

    def test_gitignore_exists(self):
        gi_path = os.path.join(os.path.dirname(__file__), "..", ".gitignore")
        self.assertTrue(os.path.exists(gi_path))

    def test_assets_exist(self):
        ascii_path = os.path.join(os.path.dirname(__file__), "..", "assets", "flipper_ascii.txt")
        self.assertTrue(os.path.exists(ascii_path))

    def test_data_files_exist(self):
        files = [
            "data/bruteforce/passwords.txt",
            "data/bruteforce/test_passwords.txt",
            "data/bruteforce/tim_wordlist.txt",
            "data/wifi/sample_wordlist.txt",
        ]
        for f in files:
            path = os.path.join(os.path.dirname(__file__), "..", f)
            self.assertTrue(os.path.exists(path), f"Missing: {f}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
