###################################################################
# value of register is dec                                        #
# key of dataMem is hex                                           #
# value of dataMem is dec                                         #
###################################################################
import msvcrt
import sys
import os

class machineCode_parser:
    word_size = 0
    dataMemory = {}
    registerFiles = {}
    register_table = {}
    current_location = 0
    # vị trí của hiện tại của break pointer
    current_brk = 0
    # vị trí bắt đầu của heap
    start_brk = 0
    # vị trí cuối cùng của heap
    end_brk = 0
    # dung de thuc thi voi file
    file = 0
    def __init__(self, registerFiles, register_table) :
        self.file = 0
        self.start_brk = 268697600
        self.end_brk = 268698108
        self.word_size = 4
        self.current_location = 4194304
        self.current_brk = self.start_brk
        self.registerFiles = registerFiles
        self.register_table = register_table

    def parse(self, instructions):
        pos = 0
        # fetch
        while True:
            # gan dia chi tiep theo cho thanh ghi pc
            self.registerFiles['pc'] = self.current_location + self.word_size
            if pos < len(instructions):
                # decode
                opcode = instructions[pos][25:]
                # lenh thuoc R-type
                if opcode == '0110011':
                    rd = self.register_table[int(instructions[pos][20:25], 2)]
                    funct3 = instructions[pos][17:20]
                    rs1 = self.register_table[int(instructions[pos][12:17], 2)]
                    rs2 = self.register_table[int(instructions[pos][7:12], 2)]
                    funct7 = instructions[pos][0:7]
                    #execute
                    self.ExecuteR(funct7, rs2, rs1, funct3, rd)

                # lenh thuoc I-type
                elif opcode == '0010011' or opcode == '0000011' or opcode == '1100111':
                    rd = self.register_table[int(instructions[pos][20:25], 2)]
                    funct3 = instructions[pos][17:20]
                    rs1 = self.register_table[int(instructions[pos][12:17], 2)]
                    imm_12bits = instructions[pos][0:12]
                    #execute
                    self.ExecuteI(opcode, funct3, rd, rs1, imm_12bits)


                # lenh thuoc U-type
                elif opcode == '0110111' or opcode == '0010111':
                    rd = self.register_table[int(instructions[pos][20:25], 2)]
                    imm_31_12 = instructions[pos][0:20]
                    # execute
                    self.ExecuteU(opcode,rd, imm_31_12)

                # lenh thuoc S-type
                elif opcode == '0100011':
                    imm_4_0 = instructions[pos][20:25]
                    funct3 = instructions[pos][17:20]
                    rs1 = self.register_table[int(instructions[pos][12:17], 2)]
                    rs2 = self.register_table[int(instructions[pos][7:12], 2)]
                    imm_11_5 = instructions[pos][0:7]
                    #excute
                    self.ExecuteS(funct3, rs1, rs2, imm_4_0, imm_11_5)

                #lenh thuoc B-type
                elif opcode == '1100011':
                    imm_4_1_11 = instructions[pos][20:25]
                    funct3 = instructions[pos][17:20]
                    rs1 = self.register_table[int(instructions[pos][12:17], 2)]
                    rs2 = self.register_table[int(instructions[pos][7:12], 2)]
                    imm_12_10_5 = instructions[pos][0:7]
                    #excute
                    self.ExecuteB(funct3, rs1, rs2, imm_4_1_11, imm_12_10_5)

                # lệnh thuộc J-type
                elif opcode == '1101111':
                    imm_20_10_1_11_19_12 = instructions[pos][0:20]
                    rd = self.register_table[(int(instructions[pos][20:25], 2))]
                    #execute
                    self.ExecuteJ(rd, imm_20_10_1_11_19_12)

                # Các lệnh syscalls
                elif opcode == '1110011':
                    #execute 
                    self.ExecuteSyscalls()
            # thoát vòng lặp
            else:
                break
            # lay dia chi cau lenh tiep theo
            self.current_location = self.registerFiles['pc']
            pos = (self.current_location - 4194304) // self.word_size
        # lưu giá trị trong thanh ghi vào data memory
        self.save_valuesR2dataMemory()
        # in kết quả ra file
        self.print_results()
    # thực thi lệnh R-type
    def ExecuteR (self, funct7, rs2, rs1, funct3, rd):
        # add
        if funct3 == '000' and  funct7 == '0000000':
            self.registerFiles[rd] = self.registerFiles[rs1] + self.registerFiles[rs2]
        # sub
        elif funct3 == '000' and funct7 == '0100000':
            self.registerFiles[rd] = self.registerFiles[rs1] - self.registerFiles[rs2]
        # xor
        elif funct3 == '100' and funct7 == '0000000':
            self.registerFiles[rd] = self.registerFiles[rs1] ^ self.registerFiles[rs2]
        # or
        elif funct3 == '110' and funct7 == '0000000':
            self.registerFiles[rd] = self.registerFiles[rs1] | self.registerFiles[rs2]
        # and
        elif funct3 == '111' and funct7 == '0000000':
            self.registerFiles[rd] = self.registerFiles[rs1] & self.registerFiles[rs2]
        # shift left logical
        elif funct3 == '001' and funct7 == '0000000':
            self.registerFiles[rd] = self.registerFiles[rs1] << self.registerFiles[rs2]
        # shift right logical
        elif funct3 == '101' and funct7 == '0000000':
            self.registerFiles[rd] = self.registerFiles[rs1] >> self.registerFiles[rs2]
        # shift right Arith
        elif funct3 == '101' and funct7 == '0100000':
            self.registerFiles[rd] = self.registerFiles[rs1] >> self.registerFiles[rs2]
        # set less than
        elif funct3 == '010' and funct7 == '0000000':
            if self.registerFiles[rs1] < self.registerFiles[rs2]:
                self.registerFiles[rd] = 1
            else:
                self.registerFiles[rd] = 0
        # set less than (U)
        elif funct3 == '011' and funct7 == '0000000':
            rs1_value = abs(self.registerFiles[rs1])
            rs2_value = abs(self.registerFiles[rs2])
            if rs1_value < rs2_value:
                self.registerFiles[rd] = 1
            else:
                self.registerFiles[rd] = 0
        # đảm bảo giá trị thanh ghi zero bằng 0
        self.Fix_registerZero()

    # Thực thi lệnh I-type
    def ExecuteI(self, opcode, funct3, rd, rs1, imm_12bits ):
        if opcode == '0010011':
            # chuyển số tức thời sang hệ thập phân
            imm = self.bin2dec(imm_12bits)
            # addi
            if funct3 == '000':
                self.registerFiles[rd] = self.registerFiles[rs1] + imm
            # xori
            elif funct3 == '100':
                self.registerFiles[rd] = self.registerFiles[rs1] ^ imm
            # ori
            elif funct3 == '110':
                self.registerFiles[rd] = self.registerFiles[rs1] | imm
            # andi
            elif funct3 == '111':
                self.registerFiles[rd] = self.registerFiles[rs1] & imm
            # shift left logical Imm
            elif funct3 == '001':
                converted = '0000000' + imm_12bits[7:]
                converted_int = self.bin2dec(converted)
                self.registerFiles[rd] = self.registerFiles[rs1] << converted_int
            # shift right logical Imm
            elif funct3 == '101':
                converted = '0000000' + imm_12bits[7:]
                converted_int = self.bin2dec(converted)
                self.registerFiles[rd] = self.registerFiles[rs1] >> converted_int
            # shift right arith Imm
            elif funct3 == '101':
                converted = '0100000' + imm_12bits[7:]
                converted_int = self.bin2dec(converted)
                self.registerFiles[rd] = self.registerFiles[rs1] >> converted_int
            # set less than Imm
            elif funct3 == '010':
                if self.registerFiles[rs1]  < imm:
                    self.registerFiles[rd] = 1
                else:
                    self.registerFiles[rd] = 0
            # set less than Imm(U)
            elif funct3 == '011':
                rs1_value = abs(self.registerFiles[rs1])
                imm = abs(imm)
                if rs1_value  < imm:
                    self.registerFiles[rd] = 1
                else:
                    self.registerFiles[rd] = 0
        # lenh jalr
        elif opcode == '1100111':
            offset = self.bin2dec(imm_12bits)
            self.registerFiles[rd] = self.registerFiles['pc'] + self.word_size
            self.registerFiles['pc'] += self.registerFiles[rs1] + offset
        # Các câu lệnh load
        elif opcode == '0000011':
            # tính giá trị address = value in[rs1] + offset(imm)
            address = hex(self.bin2dec(imm_12bits) + self.registerFiles[rs1])
            if address in self.dataMemory.keys():
                # Load Byte
                if funct3 == '000':
                    self.registerFiles[rd] = self.bin2dec(self.dec2bin(self.dataMemory[address])[24:])
                # load half
                elif funct3 == '001':
                    self.registerFiles[rd] = self.bin2dec(self.dec2bin(self.dataMemory[address])[16:])
                # load word
                elif funct3 == '010':
                    self.registerFiles[rd] = self.dataMemory[address]
                # load byte (U)
                elif funct3 == '100':
                    self.registerFiles[rd] = self.bin2dec(self.dec2bin(self.dataMemory[address])[24:], 2)
                # load half (U)
                elif funct3 == '101':
                    self.registerFiles[rd] = self.bin2dec(self.dec2bin(self.dataMemory[address])[16:], 2)
            else:
                self.registerFiles[rd] = 0

        # đảm bảo giá trị thanh ghi zero bằng 0
        self.Fix_registerZero()

    # thuc thi lenh S-type
    def ExecuteS(self, funct3, rs1, rs2, imm_4_0, imm_11_5):
        # tính address = value in rs2 + offset(imm)
        address = hex(self.bin2dec(imm_11_5 + imm_4_0) + self.registerFiles[rs1])
        # store byte
        if funct3 == '000':
            self.dataMemory[address] = self.bin2dec(self.dec2bin(self.registerFiles[rs2])[24:])
        #store half
        elif funct3 == '001':
            self.dataMemory[address] = self.bin2dec(self.dec2bin(self.registerFiles[rs2])[16:])
        #store word
        elif funct3 == '010':
            self.dataMemory[address] = self.registerFiles[rs2]
        # đảm bảo giá trị thanh ghi zero bằng 0
        self.Fix_registerZero()

    # thuc thi lenh U-type
    def ExecuteU(self, opcode, rd, imm_31_12):
        imm = self.bin2dec(imm_31_12) << 12
        if opcode == '0110111':
            self.registerFiles[rd] = imm
        elif opcode == '0010111':
            self.registerFiles[rd] = self.registerFiles['pc'] + imm
        # đảm bảo giá trị thanh ghi zero bằng 0
        self.Fix_registerZero()

    # thuc thi lenh B-type
    def ExecuteB(self, funct3, rs1, rs2, imm_4_1_11, imm_12_10_5):
        converted = imm_12_10_5[0] + imm_4_1_11[-1] + imm_12_10_5[1:] + imm_4_1_11[:-1]
        offset = self.bin2dec(converted) << 1
        # branch ==
        if funct3 == '000':
            if self.registerFiles[rs1] == self.registerFiles[rs2]:
                # tính giá trị của thanh ghi pc dựa vào offset
                self.registerFiles['pc'] = self.current_location +  offset
        # branch !=
        elif funct3 == '001':
            if self.registerFiles[rs1] != self.registerFiles[rs2]:
                # tính giá trị của thanh ghi pc dựa vào offset
                self.registerFiles['pc'] = self.current_location +  offset
        # branch <
        elif funct3 == '100':
            if self.registerFiles[rs1] < self.registerFiles[rs2]:
                # tính giá trị của thanh ghi pc dựa vào offset
                self.registerFiles['pc'] = self.current_location +  offset
        # branch >=
        elif funct3 == '101':
            if self.registerFiles[rs1] >= self.registerFiles[rs2]:
                # tính giá trị của thanh ghi pc dựa vào offset
                self.registerFiles['pc'] = self.current_location +  offset
        # branch < (U)
        elif funct3 == '110':
            rs1_value = abs(self.registerFiles[rs1])
            rs2_value = abs(self.registerFiles[rs2])
            if rs1_value < rs2_value:
                # tính giá trị của thanh ghi pc dựa vào offset
                self.registerFiles['pc'] = self.current_location +  offset
        # branch >= (U)
        elif funct3 == '110':
            rs1_value = abs(self.registerFiles[rs1])
            rs2_value = abs(self.registerFiles[rs2])
            if rs1_value >= rs2_value:
                # tính giá trị của thanh ghi pc dựa vào offset
                self.registerFiles['pc'] = self.current_location +  offset
        # đảm bảo giá trị thanh ghi zero bằng 0
        self.Fix_registerZero()
   
    # thực thi lệnh j type
    def ExecuteJ(self, rd, imm_20_10_1_11_19_12):
        imm_20 = imm_20_10_1_11_19_12[0]
        imm_10_1 = imm_20_10_1_11_19_12[1:11]
        imm_11 = imm_20_10_1_11_19_12[11]
        imm_19_12 = imm_20_10_1_11_19_12[12:]
        converted = imm_20 + imm_19_12 + imm_11 + imm_10_1
        offset = self.bin2dec(converted) << 1
        self.registerFiles[rd] = self.registerFiles['pc'] + self.word_size
        self.registerFiles['pc'] = self.current_location + offset
        # đảm bảo giá trị x0 =0
        self.Fix_registerZero()

    # execute syscall instrutions
    def ExecuteSyscalls(self) :
        # PrintInt
        if self.registerFiles['a7'] == 1:
            print(self.registerFiles['a0'])

        # PrintString
        elif self.registerFiles['a7'] == 4:
            output_user = ''
            # khởi tạo ký tự tương ứng với mỗi byte trong dataMem
            char = ''
            # địa chỉ để lấy chuỗi ra khỏi dataMem 
            address = hex(self.registerFiles['a0'])
            flag = True
            while flag:
                if address not in self.dataMemory.keys():
                    # Thoát nếu địa chỉ lấy chuỗi ko tồn tại
                    flag = False
                else:
                    # lấy dữ liệu trong word
                    data = hex(self.dataMemory[address])[2:].zfill(8)
                    for pos in range(7, -1, -2):
                        char = chr(int(data[pos-1] + data[pos], 16))
                        if char == '\0':
                            # dừng lấy ký tự nếu nó là NULL 
                            flag = False
                        else:
                            output_user += char
                    address = hex(int(address, 16) + 4) 
            #In chuỗi
            print(output_user)

        # ReadInt
        elif self.registerFiles['a7'] == 5:
            self.registerFiles['a0'] = int(input())

        # readString
        elif self.registerFiles['a7'] == 8:
            # lấy độ dài tối đa của chuỗi nhập vào trong a1
            max_length = self.registerFiles['a1'] - 1
            # nhập chuỗi 
            user_input = input()[:max_length] + '\0'
            # lấy địa chỉ chuỗi lưu vào trong dataMem 
            address = hex(self.registerFiles['a0'])
            # lưu chuỗi vào dataMem
            for char in user_input:
                if address not in self.dataMemory.keys():
                    # khởi tạo địa chỉ nếu địa chỉ chưa có
                    self.dataMemory[address] = ''
                # đẩy từng kí tự vào dataMem
                self.dataMemory[address] = hex(ord(char))[2:].zfill(2) + self.dataMemory[address]
                if len(self.dataMemory[address]) == 8:
                    self.dataMemory[address] = int(self.dataMemory[address], 16)
                    # chuyển vùng nhớ nếu word hiện tại đã đầy
                    address = hex(int(address, 16) + 4)

            if address in self.dataMemory.keys():
                self.dataMemory[address] = int(self.dataMemory[address], 16)  
            
        # Sbrk (break pointer)
        elif self.registerFiles['a7'] == 9:
            inscrement = self.registerFiles['a0']
            result = self.handle_sbrk(inscrement)
            self.registerFiles['a0'] = result

        # Exit
        elif self.registerFiles['a7'] == 10:
            sys.exit()

        # PrintChar
        elif self.registerFiles['a7'] == 11:
            # chuyển byte thấp nhất sang số nguyên
            latestB2int = self.registerFiles['a0'] & 255
            print(chr(latestB2int)) 

        # ReadChar
        elif self.registerFiles['a7'] == 12:
            # đọc một kí tự từ bàn phím
            char = msvcrt.getch().decode('utf-8')
            # lưu ký tự vừa đọc vào a0 dưới dạng số nguyên
            self.registerFiles['a0'] = ord(char)

        # Exit2
        elif self.registerFiles['a7'] == 93:
            number2exit = self.registerFiles['a0']
            sys.exit(number2exit)

        # OpenFile
        elif self.registerFiles['a7'] == 1024:
            file_name = ''
            # khởi tạo ký tự tương ứng với mỗi byte trong dataMem
            char = ''
            # địa chỉ để lấy chuỗi ra khỏi dataMem 
            address = hex(self.registerFiles['a0'])
            flag = True
            while flag:
                if address not in self.dataMemory.keys():
                    # Thoát nếu địa chỉ lấy chuỗi ko tồn tại
                    flag = False
                else:
                    # lấy dữ liệu trong word
                    data = hex(self.dataMemory[address])[2:].zfill(8)
                    for pos in range(7, -1, -2):
                        char = chr(int(data[pos-1] + data[pos], 16))
                        if char == '\0':
                            # dừng lấy ký tự nếu nó là NULL 
                            flag = False
                        else:
                            file_name += char
                    address = hex(int(address, 16) + 4) 

            if self.registerFile['a1'] == 0:
                self.registerFiles['a0'] = os.open(file_name, os.O_RDONLY)
            elif self.registerFile['a1'] == 1:
                self.registerFiles['a0'] = os.open(file_name, os.O_WRONLY | os.O_CREAT)
            elif self.registerFile['a1'] == 9:
                self.registerFiles['a0'] = os.open(file_name, os.O_APPEND)
        
        # Read from file
        elif self.registerFiles['a7'] == 63:
            # Đặt con trỏ về đầu tệp
            os.lseek(self.registerFiles['a0'], os.SEEK_SET)
            data_read = os.read(self.registerFiles['a0'], self.registerFiles['a2'])

            # lấy địa chỉ chuỗi lưu vào trong dataMem 
            address = hex(self.registerFiles['a1'])
            # lưu chuỗi vào dataMem
            for char in data_read:
                if address not in self.dataMemory.keys():
                    # khởi tạo địa chỉ nếu địa chỉ chưa có
                    self.dataMemory[address] = ''
                # đẩy từng kí tự vào dataMem
                self.dataMemory[address] = hex(ord(char))[2:].zfill(2) + self.dataMemory[address]
                if len(self.dataMemory[address]) == 8:
                    self.dataMemory[address] = int(self.dataMemory[address], 16)
                    # chuyển vùng nhớ nếu word hiện tại đã đầy
                    address = hex(int(address, 16) + 4)

            if address in self.dataMemory.keys():
                self.dataMemory[address] = int(self.dataMemory[address], 16)  
            
        # Write to file 
        elif self.registerFiles['a7'] == 64:
            data_to_write = ''
            # khởi tạo ký tự tương ứng với mỗi byte trong dataMem
            char = ''
            # địa chỉ để lấy chuỗi ra khỏi dataMem 
            address = hex(self.registerFiles['a1'])
            flag = True
            while flag:
                if address not in self.dataMemory.keys():
                    # Thoát nếu địa chỉ lấy chuỗi ko tồn tại
                    flag = False
                else:
                    # lấy dữ liệu trong word
                    data = hex(self.dataMemory[address])[2:].zfill(8)
                    for pos in range(7, -1, -2):
                        char = chr(int(data[pos-1] + data[pos], 16))
                        if len(data_to_write) == self.registerFiles['a2']:
                            # dừng lấy ký tự neu chuoi bang do dai toi da co the lay
                            flag = False
                        else:
                            data_to_write += char
                    address = hex(int(address, 16) + 4) 
            os.write(self.registerFiles['a0'], data_to_write.encode("utf-8"))
            self.registerFiles['a0'] = self.registerFiles['a2']
        
        # CloseFile
        elif self.registerFiles['a7'] == 57:
            os.close(self.registerFiles['a0'])
        
        # đảm bảo giá trị x0 =0
        self.Fix_registerZero()

    def handle_sbrk(self, increment):
        old_brk = self.current_brk
        new_brk = old_brk + increment
        # kiểm tra phạm vi truy cập vùng nhớ
        if new_brk > self.old_brk or new_brk < self.start_brk:
            print('Address does not axist!')
            sys.exit(0)
        # cập nhật địa chỉ break pointer
        self.current_brk = new_brk

        return old_brk


    def dec2bin(self, number):
        # chuyển số dec sang số bin ở dạng có dấu
        if number >= 0:
            return bin(number)[2:].zfill(32)
        else:
            return bin((1 << 32) + number)[2:]

    def bin2dec(self, number):
        # chuyển số bin sang số thập phân
            if number[0] == '0':
                return int(number, 2)
            else:
                inverted = ''.join( '1' if bit == '0' else '0' for bit in number )
                twos_complement = int(inverted, 2) +1
                return -1 * twos_complement
    def Fix_registerZero(self):
        # đảm bảo giá trị thanh ghi zero luôn bằng 0
        self.registerFiles['zero'] = 0

    def print_results(self):
        # in kết quả ra file
        file_out = open('D:\python\RiscV_ISS\Results.txt', 'w')
        # in dữ liệu thanh ghi
        for k,v in self.registerFiles.items():
            file_out.write(str(k) + ': ' + str(v) + '\n')
        file_out.write('***********************NQK***********************\n')
        # in du lieu dataMemory
        for k,v in self.dataMemory.items():
            file_out.write(str(k) + ': ' + str(v) + '\n')
        file_out.close()

    def save_valuesR2dataMemory(self):
        # khoi tao vi tri data memory
        pos = '0x90'
        # lưu các giá trị trong thanh ghi vào dataMemory
        for k,v in self.registerFiles.items():
            self.dataMemory[pos] = v
            pos = hex(int(pos, 16) + 4)     
