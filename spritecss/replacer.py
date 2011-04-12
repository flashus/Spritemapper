"Replaces references to sprites with offsetted background declarations."

from . import SpriteRef
from .css import split_declaration
from .finder import NoSpriteFound, get_background_url

def _build_pos_map(smap, placements):
    """Build a dict of sprite ref => pos."""
    return dict((n.fname, p) for (p, n) in placements)

class SpriteReplacer(object):
    def __init__(self, spritemaps):
        self._smaps = dict((sm.fname, _build_pos_map(sm, plcs))
                           for (sm, plcs) in spritemaps)

    def __call__(self, css):
        with css.open_parser() as p:
            for ev in p:
                if ev.lexeme == "declaration":
                    ev = self._replace_ev(css, ev)
                yield ev

    def _replace_ev(self, css, ev):
        (prop, val) = split_declaration(ev.declaration)
        if prop == "background":
            try:
                url = get_background_url(val)
            except NoSpriteFound:
                pass
            else:
                sref = SpriteRef(css.conf.normpath(url),
                                 source=css.fname)
                try:
                    new = self._replace_val(css, ev, sref)
                except KeyError:
                    new = val
                ev.declaration = "%s: %s" % (prop, new)
        return ev

    def _replace_val(self, css, ev, sref):
        sm_fn = css.mapper(sref)
        sm_url = css.conf.get_spritemap_url(sm_fn)
        pos = self._smaps[sm_fn][sref]

        parts = ["url('%s')" % (sm_url,), "no-repeat"]
        for r in pos:
            parts.append(("-%dpx" % r) if r else "0")
        return " ".join(parts)
