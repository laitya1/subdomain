import os
import glob
import subprocess
import xml.etree.ElementTree as ET
import csv
import platform
import requests
import shutil
import psutil

def get_cpu_info():
    """获取 CPU 信息"""
    cpu_info = {}
    cpu_info['cpu_count'] = psutil.cpu_count(logical=False)
    cpu_info['cpu_count_logical'] = psutil.cpu_count(logical=True)
    cpu_info['cpu_freq'] = psutil.cpu_freq().current
    return cpu_info


def get_memory_info():
    """获取内存信息"""
    memory_info = {}
    memory = psutil.virtual_memory()
    memory_info['total_memory'] = memory.total
    memory_info['available_memory'] = memory.available
    memory_info['used_memory'] = memory.used
    memory_info['memory_percent'] = memory.percent
    return memory_info


def get_disk_info():
    """获取磁盘信息"""
    disk_info = {}
    disk = psutil.disk_usage('/')
    disk_info['total_disk'] = disk.total
    disk_info['used_disk'] = disk.used
    disk_info['free_disk'] = disk.free
    disk_info['disk_percent'] = disk.percent
    return disk_info


def get_network_info():
    """获取网络信息"""
    network_info = {}
    network = psutil.net_io_counters()
    network_info['bytes_sent'] = network.bytes_sent
    network_info['bytes_recv'] = network.bytes_recv
    return network_info


def get_system_info():
    """获取系统信息"""
    system_info = {}
    system_info['system'] = platform.system()
    system_info['node'] = platform.node()
    system_info['release'] = platform.release()
    system_info['version'] = platform.version()
    system_info['machine'] = platform.machine()
    system_info['processor'] = platform.processor()
    return system_info

def upload_results():
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    archive_name = f'result_{current_time}'
    archive_format = 'zip'
    try:
        shutil.make_archive(archive_name, archive_format, 'OneForAll/result')
        print(f"结果文件已打包为 {archive_name}.{archive_format}")
        # 这里可以添加实际的回传逻辑，例如使用 FTP、SCP 等将打包文件上传到指定服务器
        print("模拟回传完成，你需要添加实际的上传代码到这里")
    except Exception as e:
        print(f"打包或回传结果文件时出错: {e}")
        return False
    return True

'''
target_dir 文件路径
name 文件包含那些名称
ext  文件后缀
返回文件的绝对路径
'''
def find_file(name,ext='txt',target_dir='results'):
    current_dir = os.getcwd()
    ret_current_dir = os.getcwd()
    print(current_dir)
    current_dir+="/"+target_dir
    print(current_dir)
    # 存储找到的文件路径
    found_files = []
    # 检查目录是否存在
    if os.path.exists(target_dir) and os.path.isdir(target_dir):
        # 遍历目录下的所有文件和子目录
        for root, _, files in os.walk(target_dir):
            for file in files:
                # 检查文件名是否包含指定内容且为 txt 文件
                if name in file and file.endswith(ext):
                    file_path = os.path.join(root, file)
                    found_files.append(file_path)
    else:
        print(f"指定的目录 {target_dir} 不存在。")

    # 输出找到的文件路径
    if found_files:
        print("找到以下文件：")
        for file in found_files:
            print(file)
            return ret_current_dir+"/"+file
    else:
        print("未找到符合条件的文件。")
        return None


def run_oneforall(file):
    current_path=os.getcwd()
    current_path+="/"+file
    try:
        command = f'python oneforall.py --targets {file}  --threads 50 -alive True  run '
        subprocess.run(command, shell=True, check=True)
        print("OneForAll 扫描任务执行成功")
    except subprocess.CalledProcessError as e:
        print(f"执行 OneForAll 扫描任务时出错: {e}")
        return False
    return True

"""
使用 nmap 对指定目标和端口范围进行扫描，并将结果保存为 XML 文件。
:param target: 要扫描的目标 IP 地址或网段
:param options: nmap 扫描选项，默认为 -A
:param ports: 要扫描的端口范围，默认为 1-1000
:param xml_output_file: 保存扫描结果的 XML 文件路径，默认为 scan_results.xml
:return: 若扫描成功返回 True，否则返回 False

没有使用nmap  -iL targets.txt 读取文件扫描，使用的单个ip扫描 就感觉这样好些

"""
def run_nmap_scan(target, options='-v -F --min-rate 300 --max-rate 800 -T4', ports='1-65535', xml_output_file='scan_results.xml'):
    banner="""
         __      _   __      ___      ___          __                __       __     ( )   __      ___    
  //   ) ) // ) )  ) ) //   ) ) //   ) )     //  ) ) //   / / //   ) ) //   ) ) / / //   ) ) //   ) ) 
 //   / / // / /  / / //   / / //___/ /     //      //   / / //   / / //   / / / / //   / / ((___/ /  
//   / / // / /  / / ((___( ( //           //      ((___( ( //   / / //   / / / / //   / /   //__     
                                                                                        ------------- namp is running just wait

    """
    current_path=os.getcwd()
    current_path+="/scan_results.xml"
    try:
        print(banner)
        command = f'nmap {options}  {target} -oX {xml_output_file}'
        print(command)
        subprocess.run(command, shell=True, check=True)
        print(f'Nmap 扫描完成，结果已保存到 {xml_output_file}')
        return current_path
    except subprocess.CalledProcessError as e:
        print(f'Nmap 扫描出错: {e}')
        return current_path


"""
保存当前扫描的
将 nmap 扫描生成的 XML 文件转换为 CSV 文件。
:param xml_file: 输入的 nmap 扫描结果 XML 文件路径，默认为 scan_results.xml
:param csv_file: 输出的 CSV 文件路径，默认为 scan_results.csv
:return: 若转换成功返回 True，否则返回 False
"""
def convert_nmap_xml_to_csv(xml_file='scan_results.xml', csv_file='scan_results.csv'):
    try:
        csv_file="results/"+csv_file
        # 解析 XML 文件
        tree = ET.parse(xml_file)
        root = tree.getroot()
        # 准备 CSV 文件的表头
        csv_headers = ['IP', 'Port', 'State', 'Service', 'Product', 'Version', 'OS', 'Script Output']
        # 打开 CSV 文件并写入表头
        with open(csv_file, mode='w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
            writer.writeheader()
            # 遍历每个主机
            for host in root.findall('host'):
                ip = host.find('address').get('addr')
                os_info = host.find('.//osmatch')
                os_name = os_info.get('name', '') if os_info is not None else ''

                # 遍历每个端口
                for port in host.findall('.//port'):
                    try:
                        port_id = port.get('portid')
                        state = port.find('state').get('state')
                        service = port.find('service')
                    except Exception as e:
                        port_id=""
                        state=""
                        service=""
                    # 提取服务信息
                    if service is not None:
                        product = service.get('product', '')
                        version = service.get('version', '')
                    else:
                        product = ''
                        version = ''

                    # 提取脚本扫描结果
                    script = port.find('script')
                    script_output = script.get('output', '') if script is not None else ''

                    # 写入一行数据到 CSV 文件
                    writer.writerow({
                        'IP': ip,
                        'Port': port_id,
                        'State': state,
                        'Service': service.get('name', '') if service else '',
                        'Product': product,
                        'Version': version,
                        'OS': os_name,
                        'Script Output': script_output
                    })

        print(f'XML 文件已成功转换为 {csv_file}')
        #这个不能删除文件，因为删除了后面的函数找不到文件 parse_nmap_xml_and_append_to_csv
        # try:
        #     # 删除nmap运行后产生的文件
        #     os.remove(xml_file)
        # except Exception:
        #     pass
        return True
    except FileNotFoundError:
        print(f'未找到 XML 文件: {xml_file}')
        return False
    except Exception as e:
        print(f'转换过程中出错: {e}')
        return False

"""
保存所有的结果
将 nmap 扫描生成的 XML 文件转换为 CSV 文件。
:param xml_file: 输入的 nmap 扫描结果 XML 文件路径，默认为 scan_results.xml
:param csv_file: 输出的 CSV 文件路径，默认为 all_scan_results.csv
:return: 若转换成功返回 True，否则返回 False
"""
def parse_nmap_xml_and_append_to_csv(domain,xml_file='scan_results.xml', csv_file='all_scan_results.csv'):
    try:
        csv_file = "results/" + csv_file
        # 解析 XML 文件
        tree = ET.parse(xml_file)
        root = tree.getroot()
        # 准备 CSV 文件的表头
        csv_headers = ['IP','domain', 'Port', 'State', 'Service', 'Product', 'Version', 'OS', 'Script Output']
        # 打开 CSV 文件并写入表头
        with open(csv_file, mode='a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
            writer.writeheader()
            # 遍历每个主机
            for host in root.findall('host'):
                ip = host.find('address').get('addr')
                os_info = host.find('.//osmatch')
                os_name = os_info.get('name', '') if os_info is not None else ''

                # 遍历每个端口
                for port in host.findall('.//port'):
                    try:
                        port_id = port.get('portid')
                        state = port.find('state').get('state')
                        service = port.find('service')
                    except Exception as e:
                        port_id=""
                        state=""
                        service=""

                    # 提取服务信息
                    if service is not None:
                        product = service.get('product', '')
                        version = service.get('version', '')
                    else:
                        product = ''
                        version = ''

                    # 提取脚本扫描结果
                    script = port.find('script')
                    script_output = script.get('output', '') if script is not None else ''

                    # 写入一行数据到 CSV 文件
                    writer.writerow({
                        'IP': ip,
                        'domain':domain,
                        'Port': port_id,
                        'State': state,
                        'Service': service.get('name', '') if service else '',
                        'Product': product,
                        'Version': version,
                        'OS': os_name,
                        'Script Output': script_output
                    })

        print(f'XML 文件已成功转换为 {csv_file}')
        try:
            # 删除nmap运行后产生的文件
            os.remove(xml_file)
        except Exception:
            pass
        return True
    except FileNotFoundError:
        print(f'未找到 XML 文件: {xml_file}')
        return False
    except Exception as e:
        print(f'转换过程中出错: {e}')
        return False


'''
masscan -p80,443 192.168.1.0/24 -oG results.txt
masscan -p1 -65535 192.168.1.100 -oJ results.json
masscan -p22,8080 10.0.0.0/8 -oX results.xml


nmap -sV -p1 -1000 172.16.0.0/16 -oX results.xml
nmap -A 192.168.1.10 -oJ results.json
'''

def install_nmap_linux():
    system = platform.system()
    if system != "Linux":
        print("此脚本仅适用于 Linux 系统，请在 Linux 环境下运行。")
        install_nmap_windows()#windows安装
    try:
        with open('/etc/os-release') as f:
            os_release = f.read()
            if 'Debian' in os_release or 'Ubuntu' in os_release:
                print("检测到 Debian 或 Ubuntu 系统，开始安装 nmap...")
                subprocess.run(['sudo', 'apt-get', 'update'], check=True)
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'nmap'], check=True)
            elif 'CentOS' in os_release or 'Red Hat' in os_release:
                print("检测到 CentOS 或 RHEL 系统，开始安装 nmap...")
                subprocess.run(['sudo', 'yum', 'update', '-y'], check=True)
                subprocess.run(['sudo', 'yum', 'install', '-y', 'nmap'], check=True)
            elif 'Arch' in os_release:
                print("检测到 Arch Linux 系统，开始安装 nmap...")
                subprocess.run(['sudo', 'pacman', '-Syu', '--noconfirm'], check=True)
                subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'nmap'], check=True)
            else:
                print("未识别的 Linux 发行版，无法自动安装 nmap。请手动安装。")
                return
        print("nmap 安装成功！")
        # 验证 nmap 是否安装成功
        try:
            subprocess.run(['nmap', '--version'], check=True)
            print("nmap 已成功安装并可正常使用。")
        except subprocess.CalledProcessError:
            print("nmap 安装可能存在问题，请检查。")
    except FileNotFoundError:
        print("无法找到 /etc/os-release 文件，请手动安装 nmap。")
    except subprocess.CalledProcessError as e:
        print(f"安装过程中出现错误: {e}")


def install_nmap_windows():
    temp_dir = os.environ.get('TEMP')
    installer_file = os.path.join(temp_dir, 'nmap-7.94-setup.exe')
    url="https://nmap.org/dist/nmap-7.94-setup.exe"
    try:
        print("开始下载 Nmap 安装包...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(installer_file, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print("Nmap 安装包下载完成。")
    except requests.RequestException as e:
        print(f"下载过程中出现错误: {e}")
        return False
    """
    执行 Nmap 安装程序
    :param installer_path: 本地 Nmap 安装程序的路径
    """
    try:
        print("开始安装 Nmap...")
        # 使用 subprocess 调用安装程序，/S 参数表示静默安装
        subprocess.run([installer_file, '/S'], check=True)
        print("Nmap 安装成功。")
    except subprocess.CalledProcessError as e:
        print(f"Nmap 安装失败，错误信息: {e}")
        return False
    return True

if __name__ == '__main__':
    run_oneforall("xxxsrc.txt")
    print("""
    只能用于多域名时才有存在all_subdomain_result_*.txt这个文件，
    
    """)
    subdomain=find_file("all_subdomain_result_","txt","results")
    try:
        # 以只读模式打开文件
        with open(subdomain, 'r', encoding='utf-8') as file:
            # 逐行遍历文件内容
            for line in file:
                # 去除每行末尾的换行符
                line = line.strip()
                print(line)
                try:
                    xml_path = run_nmap_scan(line)
                    convert_nmap_xml_to_csv(xml_path)
                    parse_nmap_xml_and_append_to_csv(line,xml_path)
                except Exception as e:
                    print("this machine do not has nmap ")
                    install_nmap_linux()  # 里面有windwos安装
                    try:
                        xml_path = run_nmap_scan(line)
                        convert_nmap_xml_to_csv(xml_path)
                        parse_nmap_xml_and_append_to_csv(line,xml_path)
                    except Exception as e:
                        print("this machine do not has nmap ")
                        break
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
    except Exception as e:
        print(f"读取文件时出现错误: {e}")


