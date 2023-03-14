import numpy as np
import torch


def maximum_path(neg_cent, mask):
    """Pure Python implementation.
    neg_cent: [b, t_t, t_s]
    mask: [b, t_t, t_s]
    """
    device = neg_cent.device
    dtype = neg_cent.dtype
    neg_cent = neg_cent.detach().cpu().numpy().astype(np.float32)
    path = np.zeros(neg_cent.shape, dtype=np.int32)

    for i in range(neg_cent.shape[0]):
        t_t_max = int(mask[i].sum(1)[0])
        t_s_max = int(mask[i].sum(2)[0])
        maximum_path_each(path[i], neg_cent[i], t_t_max, t_s_max)

    return torch.from_numpy(path).to(device=device, dtype=dtype)


def maximum_path_each(path, value, t_y, t_x, max_neg_val=-1e9):
    for y in range(t_y):
        for x in range(max(0, t_x + y - t_y), min(t_x, y + 1)):
            if x == y:
                v_cur = max_neg_val
            else:
                v_cur = value[y - 1, x]
            if x == 0:
                if y == 0:
                    v_prev = 0.0
                else:
                    v_prev = max_neg_val
            else:
                v_prev = value[y - 1, x - 1]
            value[y, x] += max(v_prev, v_cur)

    index = t_x - 1
    for y in range(t_y - 1, -1, -1):
        path[y, index] = 1
        if index != 0 and (index == y or value[y - 1, index] < value[y - 1, index - 1]):
            index = index - 1
