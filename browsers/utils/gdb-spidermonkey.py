class JSObjectInfo(gdb.Command):
    def __init__(self):
        super(JSObjectInfo, self).__init__ ("jsinfo", gdb.COMMAND_DATA)
        self.expr_builder = ExpressionBuilder()

    def invoke(self, pointer_jsvalue, from_tty):
        if len(pointer_jsvalue) == 0:
            print("jsinfo <taggedPointer/address/gdb expression>")
            return

        # This is either the real pointer to an object or its tagged pointer (NaN-boxing)
        is_unsigned_long = pointer_jsvalue.startswith("0xfff")
        # Doesn't look like a hex string either, try evaluating it as a GDB expression
        if not pointer_jsvalue.startswith("0x"):
            jsvalue = gdb.parse_and_eval(pointer_jsvalue)
            if jsvalue and str(jsvalue.type) == "JS::Value":
                pointer_jsvalue = str(self.eval("js::value", jsvalue.address, ".asBits_"))
                is_unsigned_long = True
            else:
                print("[-] Couldn't evaluate argument, got: " + str(address))
                return

        if is_unsigned_long:
            as_int = int(pointer_jsvalue, 16)
            print("[*] Parsing JS::Value at     " + pointer_jsvalue)
            tag = (((0xffff << 48) & as_int) >> 47) & 0xf
            tagName = self.tag_to_name(tag)
            print("[*] Tag is                   " + tagName)
            payload = ((2 ** 48) - 1) & as_int
            payload = hex(payload)
            print("[*] Payload is               " + payload)
        else:
            payload = pointer_jsvalue

        print("[*] Class is                 " + str(self.eval("class", payload)))
        className = self.eval("className", payload).string()
        print("[*] Class name is            " + className)
        if className == 'Array':
            length = int(self.eval("array", payload, ".length()"))
            print("[*] Length:                  " + str(length))
            print("\nElements:")
            as_array = self.expr_builder.get("array").value(payload)
            gdb.execute("x/%dx %s.elements_" % (length, as_array))

        classOps = self.expr_builder.get("classops")
        print("\n[*] JSClassOps at            " + str(gdb.parse_and_eval(classOps.location(payload))))
        if gdb.parse_and_eval(classOps.value(payload)).address:
            print("[*] JSClassOps:")
            gdb.execute("p %s" % classOps.value(payload))

        return pointer_jsvalue

    def eval(self, expr, address, append=""):
        return gdb.parse_and_eval(self.expr_builder.get(expr).value(address) + append)


    '''
    As per git commit 2e7e5f93bc63f7f1afacaab2423012f6d859cf6a
    enum JSValueType : uint8_t {
      JSVAL_TYPE_DOUBLE = 0x00,
      JSVAL_TYPE_INT32 = 0x01,
      JSVAL_TYPE_BOOLEAN = 0x02,
      JSVAL_TYPE_UNDEFINED = 0x03,
      JSVAL_TYPE_NULL = 0x04,
      JSVAL_TYPE_MAGIC = 0x05,
      JSVAL_TYPE_STRING = 0x06,
      JSVAL_TYPE_SYMBOL = 0x07,
      JSVAL_TYPE_PRIVATE_GCTHING = 0x08,
      JSVAL_TYPE_BIGINT = 0x09,
      JSVAL_TYPE_OBJECT = 0x0c,

      // This type never appears in a Value; it's only an out-of-band value.
      JSVAL_TYPE_UNKNOWN = 0x20
    };
    '''
    def tag_to_name(self, tag):
        if tag == 0x0:
            return "double"
        elif tag == 0x1:
            return "int32"
        elif tag == 0x2:
            return "boolean"
        elif tag == 0x3:
            return "undefined"
        elif tag == 0x4:
            return "null"
        elif tag == 0x5:
            return "magic"
        elif tag == 0x6:
            return "string"
        elif tag == 0x7:
            return "symbol"
        elif tag == 0x8:
            return "privateGcThing"
        elif tag == 0x9:
            return "bigInt"
        elif tag == 0xc:
            return "object"
        elif tag == 0x20:
            return "unknown"
        else:
            return "[-] UNKNOWN TYPE: " + str(tag)



def expr(expr):
    return Expression(expr)

class Expression:
    def __init__(self, expr_format):
        self.value = lambda addr: expr_format % addr
        self.location = lambda addr: "&" + expr_format % addr


class ExpressionBuilder(gdb.Command):
    expression_types = {
            "js::value": expr("((JS::Value)*%s)"),
            "object": expr("((JSObject)*%s)"),
            "className": expr("((JSObject)*%s).groupRaw().clasp_.name"),
            "array": expr("(('js::ArrayObject')*%s)"),
            "classops": expr("(JSClassOps)(*((JSObject)*%s).groupRaw().clasp_.cOps)"),
            "classops*": expr("((JSObject)*0x3d4a94c935e0).groupRaw().clasp_.cOps"),
            "class": expr("((JSObject)*%s).getClass()")
    }

    def __init__(self):
        super(ExpressionBuilder, self).__init__("buildexp", gdb.COMMAND_NONE)

    def get(self, exp_type):
        if not exp_type in self.expression_types.keys():
            return None
        return self.expression_types[exp_type]

    def invoke(self, args, from_tty): #exp_type, pointer_jsvalue):
        argv = gdb.string_to_argv(args)
        if len(argv) != 2:
            print('[-] buildexp <expression_type> <address>')
            return

        exp_type, pointer_jsvalue = argv
        if type(exp_type) == gdb.Value:
            exp_type = exp_type.string()
    
        expr = self.get(exp_type)
        if expr == None:
            print("[-] Expression type must be one of: ")
            for key in self.expression_types:
                print(key)

            print("\n")
            return

        print(self.expression_types[exp_type].value(pointer_jsvalue))






JSObjectInfo()
ExpressionBuilder()
