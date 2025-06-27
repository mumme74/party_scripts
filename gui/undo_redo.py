

class Undo:
    _instances = []
    _current = None
    def __init__(self, prj_wrapped):
        Undo._instances.append(self)
        Undo._current = self
        self.prj_wrapped = prj_wrapped
        self._stack = []
        self._pos = -1
        self._disabled = False
        self._transaction = False
        self._transaction_list = []
    
    @classmethod
    def ref(cls):
        return cls._current
    
    @classmethod
    def set_current(cls, undo):
        if isinstance(undo, int):
            cls._current = Undo._instances[undo]
        else:
            cls._current = undo
    
    def start_transaction(self):
        self._transaction = True

    def commit_transaction(self):
        self._stack.append(self._transaction_list)

        self._pos += 1
        self.clear(self._pos)

    def revert_transaction(self):
        self._transaction_list.clear()
        self._transaction = False

    def store_change(self, var, old_vlu, new_vlu):
        if self._disabled:
            return
        
        self.clear(self._pos+1)
        self._pos += 1
        
        self._stack.append({
            'var': var, 
            'new_vlu': new_vlu, 
            'old_vlu': old_vlu
        })
        
    def clear(self, to_pos=0):
        while to_pos < len(self._stack):
            self._stack.pop()
        self._pos = to_pos-1

    def undo_cnt(self):
        return self._pos
    
    def redo_cnt(self):
        return len(self._stack) - self._pos
    
    def undo(self):
        if self._pos >= 0:
            dis = self._disabled
            self._disabled = True
            itm = self._stack[self._pos]
            if isinstance(itm, list):
                for u in itm:
                    u['var'].set(itm['old_vlu'])
            else:
                itm['var'].set(itm['old_vlu'])
            self._pos -= 1
            self._disabled = dis

    def redo(self):
        if self._pos < len(self._stack)-1:
            dis = self._disabled
            self._disabled = True
            itm = self._stack[self._pos]
            if isinstance(itm, list):
                for r in itm:
                    r['var'].set['new_vlu']
            else:
                itm['var'].set(itm['new_vlu'])
            self._pos += 1
            self._disabled = dis

    def disabled(self):
        return self._disabled

    def set_disabled(self, dis):
        self._disabled = dis
