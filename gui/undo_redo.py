import copy

class UndoTransaction:
    """
    Start a scopeguard undo transaction
    with a with statment
     like:
       with UndoTransaction(undo):
          ... do stuff

          # to revert:
          ... undo.commit_transaction

      Transaction is automatically commited if not reverted
    """
    def __init__(self, undo):
        self._undo = undo
    def __enter__(self):
        self._undo.start_transaction()
        return self
    def __exit__(self, *args):
        self._undo.commit_transaction()


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
        self._dis = False
    def __enter__(self):
        self._dis = self._undo._disabled
        self._undo._disabled = True
        return self
    def __exit__(self, *args):
        # might be nested, handle that
        self._undo._disabled = self._dis

class UndoSnapshot:
    """
    Used to take a snaphot of an objects values
    Not for wrap objects. Only real backend py objects
    Take a snapshot before any changes, to be able to replay later

    NOTE: It only works on reference objects,
          not scalars such as int, str, etc
    """
    def __init__(self, snap_obj):
        self._snap_obj = snap_obj
        self._before = copy.deepcopy(snap_obj)

    def commit(self):
        Undo.ref().store_snapshot(self)

    def _on_store(self):
        self._after = copy.deepcopy(self._snap_obj)

    def back(self):
        self._restore(self._before)

    def forward(self):
        self._restore(self._after)

    def _restore(self, src):
        assert type(src) == type(self._snap_obj)
        def do(sobj, src, lvl):
            if isinstance(src, list):
                sobj.clear()
                sobj.extend(src)
                return

            if hasattr(src, '__dict__'):
                src = src.__dict__
                sobj = sobj.__dict__

            keys_t = list(src.keys())
            keys_s = list(sobj.keys())
            for k in keys_t:
                if lvl < 2 and sobj[k] is not None and \
                    (hasattr(src[k], '__dict__') or \
                     isinstance(src[k], (list, dict))):
                    do(sobj[k], src[k], lvl+1)
                else:
                    sobj[k] = src[k]
                if k in keys_s:
                    keys_s.pop(keys_s.index(k))

            # remove old keys
            for k in keys_s:
                del sobj[k]
        do(self._snap_obj, src, 0)


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
        self._transactions = 0
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
        self._transactions += 1

    def commit_transaction(self):
        self._transactions -= 1
        if self._transactions > 0:
            return False

        self._pos += 1
        self.clear(self._pos+1)

        self._stack.append(self._transaction_list)
        self._transaction_list = []

        self.master.event_generate('<<UndoChanged>>')

        return True

    def revert_transaction(self):
        self._transactions -= 1
        if self._transactions > 0:
            return False

        self._transaction_list.clear()

        return True

    def store_snapshot(self, snap):
        assert isinstance(snap, UndoSnapshot)

        if self._disabled:
            return

        snap._on_store()

        if self._transactions > 0:
            self._transaction_list.append(snap)
            return

        self.clear(self._pos+1)
        self._pos += 1

        self._stack.append(snap)
        self.master.event_generate('<<UndoChanged>>')

    def store_change(self, var, old_vlu, new_vlu):
        if self._disabled:
            return

        store_obj = {
            'var': var,
            'new_vlu': new_vlu,
            'old_vlu': old_vlu
        }

        if self._transactions > 0:
            self._transaction_list.append(store_obj)
            return

        self.clear(self._pos+1)
        self._pos += 1

        self._stack.append(store_obj)
        self.master.event_generate('<<UndoChanged>>')

    def clear(self, to_pos=0):
        while to_pos < len(self._stack):
            self._stack.pop()
        self._pos = to_pos-1

    def undo_cnt(self):
        return self._pos+1

    def redo_cnt(self):
        return len(self._stack) - self._pos-1

    def _do_undo(self, itm):
        if isinstance(itm, UndoSnapshot):
            itm.back()
        else:
            itm['var'].set(itm['old_vlu'])

    def _do_redo(self, itm):
        if isinstance(itm, UndoSnapshot):
            itm.forward()
        else:
            itm['var'].set(itm['new_vlu'])

    def undo(self):
        if self._pos >= 0:
            with UndoDisable(self):
                itm = self._stack[self._pos]
                if isinstance(itm, list):
                    for u in itm:
                        self._do_undo(u)
                else:
                    self._do_undo(itm)
                self._pos -= 1
            self.master.event_generate('<<Undo>>')

    def redo(self):
        if self._pos < len(self._stack)-1:
            with UndoDisable(self):
                itm = self._stack[self._pos]
                if isinstance(itm, list):
                    for r in itm:
                        self._do_redo(r)
                else:
                    self._do_redo(itm)
                self._pos += 1
            self.master.event_generate('<<Redo>>')
