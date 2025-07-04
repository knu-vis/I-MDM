from torch.utils.data import DataLoader, ConcatDataset
from data_loaders.tensors import collate as all_collate
from data_loaders.tensors import collate_img as all_collate_img
from data_loaders.tensors import t2m_collate

def get_dataset_class(name):
    if name == "amass":
        from .amass import AMASS
        return AMASS
    elif name == "uestc":
        from .a2m.uestc import UESTC
        return UESTC
    elif name == "humanact12":
        from .a2m.humanact12poses import HumanAct12Poses
        return HumanAct12Poses
    elif name == "ntu120":
        from .a2m.ntu120_motion import NTU120Motion
        return NTU120Motion
    elif name == "ntu120_tp":
        from .a2m.ntu120_motion_twoperson import NTU120Motion_TP
        return NTU120Motion_TP
    elif name == "ntu120_tp_sk":
        from .a2m.ntu120_motion_twoperson_skateformer import NTU120Motion_TP_SK
        return NTU120Motion_TP_SK
    elif name == 'ntu120_tp_img':
        from .a2m.ntu120_motion_twoperson_with_image import NTU120Motion_TP_IMG
        return NTU120Motion_TP_IMG
    elif name == "humanml":
        from data_loaders.humanml.data.dataset import HumanML3D
        return HumanML3D
    elif name == "kit":
        from data_loaders.humanml.data.dataset import KIT
        return KIT
    else:
        raise ValueError(f'Unsupported dataset name [{name}]')

def get_collate_fn(name, hml_mode='train'):
    if hml_mode == 'gt':
        from data_loaders.humanml.data.dataset import collate_fn as t2m_eval_collate
        return t2m_eval_collate
    if name in ["humanml", "kit"]:
        return t2m_collate
    elif name in ['ntu120_tp_img']:
        return all_collate_img
    else:
        return all_collate


def get_dataset(name, num_frames, split='train', hml_mode='train', num_actions=None,
                single_only=False, two_only=False, one_motion=False, pkldatafilepath=None, ntu_mode='xsub'):
    DATA = get_dataset_class(name)
    if name in ["humanml", "kit"]:
        dataset = DATA(split=split, num_frames=num_frames, mode=hml_mode)
    elif name in ['ntu120', 'ntu120_tp', 'ntu120_tp_img', 'ntu120_tp_sk']:
        dataset = DATA(split=split, num_frames=num_frames, 
                       num_actions=num_actions, single_only=single_only, two_only=two_only,
                       one_motion=one_motion, pkldatafilepath=pkldatafilepath, ntu_mode=ntu_mode)
    else:
        dataset = DATA(split=split, num_frames=num_frames)
    return dataset


def get_dataset_loader(name, batch_size, num_frames, split='train', hml_mode='train', num_actions=None,
                       single_only=False, two_only=False, one_motion=False, pkldatafilepath=None, ntu_mode='xsub'):
    dataset = get_dataset(name, num_frames, split, hml_mode, num_actions, single_only, two_only, 
                          one_motion, pkldatafilepath, ntu_mode)
    collate = get_collate_fn(name, hml_mode)

    loader = DataLoader(
        dataset, batch_size=batch_size, shuffle=True if split == 'train' else False,
        num_workers=8, drop_last=False, collate_fn=collate
    )

    return loader


def concat_dataset_loader(name, batch_size, num_frames, ds1, ds2, split='train', hml_mode='train', 
                          num_actions=None, single_only=False, one_motion=False, pkldatafilepath=None):
    collate = get_collate_fn(name, hml_mode)
    
    combined_dataset = ConcatDataset([ds1, ds2])
    loader = DataLoader(
        combined_dataset, batch_size=batch_size, shuffle=True if split == 'train' else False,
        num_workers=8, drop_last=False, collate_fn=collate
    )
    
    return loader