

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
            node = call_stack[0]
            if node not in data_stack.keys(): # probs shouldt use a dict, todo work out smarter way
                data_stack[node] = Data(node)
            if data_stack[node].empty:
                #i = data_stack[node].empty
                while data_stack[node].empty:
                    i = data_stack[node].empty.pop()
                    next_node = node.inputs[i[0]].next_plug
                    if not next_node:
                        node.set_flag("missing input")
                        return
                    next_node = next_node.node
                    if next_node not in data_stack.keys():
                        data_stack[next_node] = Data(next_node)
                    if not data_stack[next_node].has_eval:
                        call_stack.insert(0, next_node)
                        pointer += 1
            elif data_stack[node].has_eval:
                #make input dict
                call_stack.pop(0)
                pointer -= 1
                for i in node.outputs:
                    if i.next_plug.node not in data_stack:
                        data_stack[i.next_plug.node] = Data(node)

                        call_stack.append(i.next_plug.node)
                        pointer += 1
                    try:
                        data_stack[i.next_plug.node].inputs[i.next_plug.index] = data_stack[i.node].outputs[i.name]
                    except KeyError:
                        node.set_flag("unknown node output")
                        return

            else:
                data_node = data_stack[node]

                for n in node.outputs:
                    if n.node is None:
                        node.set_flag("missing data output")
                        return

                args = Arguments()
                for d, name in zip(data_node.inputs, node.inputs):
                    if d is None:
                        node.set_flag("missing data input")
                        return
                    args[name.name] = d
                result = node.eval(args)
                data_node.has_eval = True
                for k, v in result.output.items():
                    data_node.outputs[k] = v
                for i in node.outputs:
                    if not i.next_plug:
                        node.set_flag("missing output")
                        return
                    next_node = i.next_plug.node
                    if type(next_node) is None:
                        node.set_flag("missing output")
                        return
                    if next_node not in data_stack.keys():  # probs shouldt use a dict, todo work out smarter way
                        data_stack[next_node] = Data(next_node)
                        call_stack.append(next_node)
                        pointer += 1


class Arguments(dict):

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value


class Data:
    def __init__(self, node):
        self.inputs = [None for i in node.inputs]
        self.empty = list(enumerate(node.inputs))
        self.outputs = ((i, None) for i in node.outputs)
        self.outputs = dict(self.outputs)
        self.has_eval = False


class Result:
    def __init__(self, *args, exception=False, **kwargs):
        self.__dict__["output"] = kwargs
        self.__dict__["exception"] = exception

    def __getattr__(self, attr):
        print(attr)
        return self.output[attr]

    def __setattr__(self, attr, value):
        self.output[attr] = value











