def create_key(template, outtype=("nii",), annotation_classes=None):
    if template is None or not template:
        raise ValueError("Template must be a valid format string")
    return template, outtype, annotation_classes


def infotodict(seqinfo):

    # create keys for the different images
    # anatomical images
    t1w = create_key("sub-{subject}/{session}/anat/sub-{subject}_{session}_T1w")
    t2w = create_key("sub-{subject}/{session}/anat/sub-{subject}_{session}_T2w")

    # rsfMRI images
    func_rest = create_key(
        "sub-{subject}/{session}/func/sub-{subject}_{session}_task-rest_bold"
    )

    # fieldmap images
    fmap_mag = create_key(
        "sub-{subject}/{session}/fmap/sub-{subject}_{session}_magnitude"
    )

    fmap_phase = create_key(
        "sub-{subject}/{session}/fmap/sub-{subject}_{session}_phasediff"
    )

    # the B0 AP image is saved in fmap as it will be used to correct the distortions in the DWI
    fmap_rev_phase = create_key(
        "sub-{subject}/{session}/fmap/sub-{subject}_{session}_dir-AP_epi"
    )

    # dwi images
    dwi = create_key("sub-{subject}/{session}/dwi/sub-{subject}_{session}_dir-PA_dwi")

    # create empty info dictionary
    info = {
        t1w: [],
        t2w: [],
        dwi: [],
        fmap_rev_phase: [],
        fmap_mag: [],
        fmap_phase: [],
        func_rest: [],
    }

    # loop over all the DICOM series filtering by protocol names, series description etc ...
    for seq in seqinfo:
        # To exclude t1_mprage_sag_p3_iso_MPR etc... add an exact series description match
        if (seq.protocol_name == "t1_mprage_sag_p3_iso") and (
            seq.series_description == "t1_mprage_sag_p3_iso"
        ):
            info[t1w].append(seq.series_id)

        if seq.protocol_name == "t2_space_tra_p4_iso":
            info[t2w].append(seq.series_id)

        if seq.protocol_name == "ep2d_bold_tra_s8_rsfMRI":
            info[func_rest].append(seq.series_id)

        if seq.protocol_name == "gre_field_mapping":
            if len(seq.image_type) == 4:
                if seq.image_type[2] == "M":
                    info[fmap_mag] = [seq.series_id]

        if seq.protocol_name == "gre_field_mapping":
            if len(seq.image_type) == 4:
                if seq.image_type[2] == "P":
                    info[fmap_phase] = [seq.series_id]

        if (seq.protocol_name == "ep2d_diff_tra_s3_PA") and (
                seq.series_description == "ep2d_diff_tra_s3_PA"
        ):
            info[dwi].append(seq.series_id)

        if seq.protocol_name == "ep2d_diff_tra_s3_AP":
            info[fmap_rev_phase] = [seq.series_id]

    # generate an error message if incorrect number of scans are found
    msg = []

    if len(info[t1w]) != 1:
        msg.append("WARNING: Incorrect number of T1w scans")
    if len(info[t2w]) != 1:
        msg.append("WARNING: Incorrect number of T2w scans")
    if len(info[func_rest]) != 1:
        msg.append("WARNING: Incorrect number of rsfMRI scans")
    if len(info[dwi]) != 1:
        msg.append("WARNING: Incorrect number of dwi_PA scans")
    if len(info[fmap_rev_phase]) != 1:
        msg.append("WARNING: Incorrect number of b0_AP scans")
    if len(info[fmap_mag]) != 1:
        msg.append("WARNING: Incorrect number of fieldmap magnitude scans")
    if len(info[fmap_phase]) != 1:
        msg.append("WARNING: Incorrect number of fieldmap phase-difference scans")

    # If there is an error, a message will be shown and no NIfTI files will be generated for the subject.
    if msg:
        raise ValueError("\n".join(msg))

    return info
