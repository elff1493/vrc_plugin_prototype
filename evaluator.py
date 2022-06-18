

class Evaluator:
    def __init__(self):
        self.batches = []


    def thread(self):
        pass

    def worker(self):
        for i in self.spawn:
            self.eval(i)

    def eval(self, spawn_node):

        call_stack = [spawn_node]
        data_stack = {}
        pointer = 0
        while call_stack:
            node = call_stack[pointer]
            if node not in data_stack: # probs shouldt use a dict, todo work out smarter way
                data_stack[node] = Data(node)
            if not data_stack[node].empty:
                i = 1
                while i:
                    i = data_stack[node].empty.pop()
                    next_node = node.inputs[i[0]].node
                    if not next_node:
                        node.set_flag("missing input")
                        return
                    call_stack.append(next_node)
                    pointer += 1
            elif data_stack[node].has_eval:
                #make input dict


                for i in node.outputs:
                    if i.node not in data_stack:
                        data_stack[node] = Data(node)
                    call_stack.append(i.node)
                    pointer += 1

                    data_stack[i.node].inputs[i.index] = data_stack[i.node].outputs[i.name]
            else:
                data_node = data_stack[node]
                data = {}
                for d, name in zip(data_node.inputs, node.inputs):
                    if d is None:
                        node.set_flag("missing data input")
                        return
                    data[name] = d
                result = node.eval(data)
                for k, v in result.output.items():
                    node.outputs[k] = v







class Data:
    def __init__(self, node):
        self.inputs = (None for i in node.inputs)
        self.empty = list(enumerate(node.inputs))
        self.outputs = ((i, None) for i in node.outputs)
        self.outputs = dict(self.outputs)
        self.has_eval = False

class Result:
    def __init__(self, *args, exception=False, **kwargs):
        self.output = kwargs
        self.exception = exception












