

class machineCode_parser:
    word_size = 0
    dataMemory = {}
    registerFiles = {}
    register_table = {}
    current_location = 0

    def __init__(self, registerFiles, register_table) :
        self.word_size = 4
        self.current_location = 4194304
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

            # thoát vòng lặp
            else:
                break
            # lay dia chi cau lenh tiep theo
            self.current_location = self.registerFiles['pc']
            pos = (self.current_location - 4194304) // self.word_size
        # lưu giá trị trong thanh ghi vào data memory
        self.save_values2dataMemory()
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
        file_out = open('Results.txt', 'w')
        # in dữ liệu thanh ghi
        for k,v in self.registerFiles.items():
            file_out.write(str(k) + ': ' + str(v) + '\n')
        file_out.write('***********************NQK***********************\n')
        # in du lieu dataMemory
        for k,v in self.dataMemory.items():
            file_out.write(str(k) + ': ' + str(v) + '\n')
        file_out.close()

    def save_values2dataMemory(self):
        # khoi tao vi tri data memory
        pos = '0x90'
        # lưu các giá trị trong thanh ghi vào dataMemory
        for k,v in self.registerFiles.items():
            self.dataMemory[pos] = v
            pos = hex(int(pos, 16) + 4)

            
