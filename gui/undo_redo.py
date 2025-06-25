

class Undo:
    def __init__(self, prj_wrapped):
        Undo._instance = self
        self.prj_wrapped = prj_wrapped
        self._stack = []
        self._pos = -1
        self._mychange = False
        self._disabled = False
    
    @classmethod
    def ref(cls):
        return cls._instance

    def store_change(self, var, old_vlu, new_vlu):
        if self._disabled:
            return
        
        if self._mychange:
            self._mychange = False
            return # abort my own change from redo/undo action
        
        self._pos += 1
        self.clear(self._pos)
        
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
            self._mychange = True
            itm = self._stack[self._pos]
            itm['var'].set(itm['old_vlu'])
            self._pos -= 1

    def redo(self):
        if self._pos < len(self._stack)-1:
            self._mychange = True
            self._pos += 1
            itm = self._stack[self._pos]
            itm['var'].set(itm['new_vlu'])

    def set_disabled(self, dis):
        self._disabled = dis
