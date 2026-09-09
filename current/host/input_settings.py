"""Rev G per-channel bias and active-state wire encoding."""
MODES = ('push-pull', 'npn', 'pnp', 'float', 'keeper')
ACTIVE = ('high', 'low', 'driven', 'floating', 'not-high', 'not-low')
DEFAULT_ACTIVE = ('high', 'low', 'high', 'driven', 'high')

def unpack_settings(word):
    if not isinstance(word, int) or not 0 <= word < (1 << 18):
        raise ValueError('Reserved input configuration bits')
    modes = [(word >> (3*i)) & 7 for i in range(3)]
    active = [(word >> (9+3*i)) & 7 for i in range(3)]
    if any(m >= len(MODES) for m in modes) or any(a >= len(ACTIVE) for a in active):
        raise ValueError('Invalid input mode or active state')
    return dict(modes=[MODES[m] for m in modes], active=[ACTIVE[a] for a in active])

def pack_settings(modes, active=None):
    if isinstance(modes, str): modes = modes.split(',')
    if isinstance(active, str): active = active.split(',')
    if len(modes) != 3: raise ValueError('Specify three input modes')
    codes = [MODES.index(m) for m in modes]
    if active is None: active = [DEFAULT_ACTIVE[m] for m in codes]
    if len(active) != 3: raise ValueError('Specify three active states')
    return sum(m << (3*i) for i,m in enumerate(codes)) | sum(ACTIVE.index(a) << (9+3*i) for i,a in enumerate(active))
