

class UndoTransaction:
    """
    Start a scopeguard undo transaction
    with a with statment
     like: 
       with UndoTransaction(undo):
          ... do stuff

          # remeber to:
          ... undo.commit_transaction 
     
      Transaction reverted if not yet 
      committed
    """
    def __init__(self, undo):
        self._undo = undo
    def __enter__(self):
        self._undo.start_transaction()
        return self
    def __exit__(self, *args):
        if self._undo._transaction:
            self._undo.revert_transaction()


class UndoDisable:
    """
    Temporarily disable a undo
    with a with statment
     like: 
       with UndoDisable(undo):
          ... do stuff
     
      undo enabled again
    """
    def __init__(self, undo):
        self._undo = undo
    def __enter__(self):
        self._undo._disabled = True
        return self
    def __exit__(self, *args):
        self._undo._disabled = False

class Undo:
    _instances = []
    _current = None
    def __init__(self, master, prj_wrapped):
        Undo._instances.append(self)
        Undo._current = self
        self.master = master
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
        self.master.event_generate('<<UndoChanged>>')
        
    def clear(self, to_pos=0):
        while to_pos < len(self._stack):
            self._stack.pop()
        self._pos = to_pos-1

    def undo_cnt(self):
        return self._pos+1
    
    def redo_cnt(self):
        return len(self._stack) - self._pos-1
    
    def undo(self):
        if self._pos >= 0:
            with UndoDisable(self):
                itm = self._stack[self._pos]
                if isinstance(itm, list):
                    for u in itm:
                        u['var'].set(itm['old_vlu'])
                else:
                    itm['var'].set(itm['old_vlu'])
                self._pos -= 1
            self.master.event_generate('<<Undo>>')

    def redo(self):
        if self._pos < len(self._stack)-1:
            with UndoDisable(self):
                itm = self._stack[self._pos]
                if isinstance(itm, list):
                    for r in itm:
                        r['var'].set['new_vlu']
                else:
                    itm['var'].set(itm['new_vlu'])
                self._pos += 1
            self.master.event_generate('<<Redo>>')
