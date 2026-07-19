"""
Rename Blender objects to SamplePet01 naming standard.
Usage: python rename_to_standard.py <model_name> <armature_name> <part1:part2:...>

Example:
  python rename_to_standard.py paopao paopao body.002:body hands.003:hands
  
This renames:
  paopao -> paopao_Armature
  body.002 -> paopao_body
  hands.003 -> paopao_hands
"""

import sys, json, socket

def main():
    if len(sys.argv) < 3:
        print("Usage: python rename_to_standard.py <model_name> <armature_name> <old_part:new_part>...")
        print("Example: python rename_to_standard.py paopao paopao body.002:body hands.003:hands")
        return 1

    model_name = sys.argv[1]
    armature_name = sys.argv[2]

    code_lines = [
        "import bpy",
        f"arm = bpy.data.objects.get('{armature_name}')",
        f"if arm:",
        f"    arm.name = '{model_name}_Armature'",
        f"    print(f'Armature renamed: {armature_name} -> {model_name}_Armature')",
    ]

    for arg in sys.argv[3:]:
        if ':' in arg:
            old_name, new_part = arg.split(':', 1)
            new_name = f"{model_name}_{new_part}"
            code_lines.append(f"obj = bpy.data.objects.get('{old_name}')")
            code_lines.append(f"if obj:")
            code_lines.append(f"    obj.name = '{new_name}'")
            code_lines.append(f"    print(f'  {{obj.type}}: {old_name} -> {new_name}')")

    code_lines.append("print('Done')")
    code = "\n".join(code_lines)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect(('127.0.0.1', 9876))
    cmd = json.dumps({'type': 'execute_code', 'params': {'code': code}})
    sock.sendall(cmd.encode() + b'\n')
    data = b''
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        except socket.timeout:
            break
    sock.close()
    resp = json.loads(data.decode('utf-8'))
    if resp.get('status') == 'success':
        print(resp['result'].get('result', ''))
    else:
        print(f"Error: {resp.get('message')}")
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
