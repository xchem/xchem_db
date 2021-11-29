# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals
from django.db import models
from django_mysql.models import ListTextField
import os

class Target(models.Model):
    target_name = models.CharField(max_length=255, blank=False, null=False, unique=True, db_index=True)
    uniprot_id = models.CharField(max_length=255, blank=True, null=True)
    alias = models.CharField(max_length=255, blank=True, null=True)
    pl_reference = models.FileField(max_length=500, blank=True)
    pl_monomeric = models.BooleanField(default=False)
    pl_reduce_reference_frame = models.BooleanField(default=True)
    pl_covalent_attachments = models.BooleanField(default=True) 
    pl_additional_headers = models.TextField(blank=True, null=False)
    pl_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'target'


class Compounds(models.Model):
    smiles = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    compound_string = models.CharField(max_length=255, blank=True, null=True, db_index=True) # Zcode...

    class Meta:
        db_table = 'compound'
        unique_together = ['smiles', 'compound_string']

class Reference(models.Model):
    reference_pdb = models.CharField(
        max_length=255, null=True, default='not_assigned', unique=True)

    class Meta:
        db_table = 'reference'


class Proposals(models.Model):
    # TODO - can we refactor this for title
    proposal = models.CharField(max_length=255, blank=False, null=False, unique=True, db_index=True)
    title = models.CharField(max_length=10, blank=True, null=True)
    fedids = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'proposals'


class SoakdbFiles(models.Model):
    filename = models.CharField(max_length=255, blank=False, null=False, unique=True)
    modification_date = models.BigIntegerField(blank=False, null=False)
    proposal = models.ForeignKey(Proposals, on_delete=models.CASCADE, unique=False)
    visit = models.TextField(blank=False, null=False)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'soakdb_files'
        

    
class Crystal(models.Model):
    crystal_name = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    target = models.ForeignKey(Target, on_delete=models.CASCADE)
    compound = models.ManyToManyField(Compounds, through='CrystalCompoundPairs')
    visit = models.ForeignKey(SoakdbFiles, on_delete=models.CASCADE)

    # model types
    PREPROCESSING = 'PP'
    PANDDA = 'PD'
    REFINEMENT = 'RE'
    COMPCHEM = 'CC'
    DEPOSITION = 'DP'

    CHOICES = (
        (PREPROCESSING, 'preprocessing'),
        (PANDDA, 'pandda'),
        (REFINEMENT, 'refinement'),
        (COMPCHEM, 'comp_chem'),
        (DEPOSITION, 'deposition')
    )

    status = models.CharField(
        choices=CHOICES, max_length=2, default=PREPROCESSING)
    well = models.CharField(max_length=4,  blank=True, null=True)
    # double-check if it shouldn't be float
    echo_x = models.IntegerField(blank=True, null=True)
    # double-check if it shouldn't be float
    echo_y = models.IntegerField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('crystal_name', 'visit',)
        db_table = 'crystal'

class CrystalCompoundPairs(models.Model):
    crystal = models.ForeignKey(Crystal, on_delete=models.CASCADE)
    compound = models.ForeignKey(Compounds, on_delete=models.CASCADE)
    product_smiles = models.CharField(max_length=255, blank=True, null=True) # Need to find way of specifying this...
    
    class Meta:
        db_table = 'crystal_compound_pairs'
    
# TODO: think about how to actually do this
# class CompoundCombination(models.Model):
#     '''for combisoaks and cocktails'''
#     visit = models.ForeignKey(
#         Visit, blank=True, null=True, on_delete=models.PROTECT)
#     number = models.IntegerField(blank=True, null=True)
#     compounds = models.ManyToManyField(SpaCompound)
#     related_crystals = models.CharField(max_length=64, null=True, blank=True)
#     '''if a combination is based on the result of the previous soak,
# 	the crystals based on which the combination is created are recorder
# 	as related_crystals'''


class DataProcessing(models.Model):
    auto_assigned = models.TextField(blank=True, null=True)
    cchalf_high = models.FloatField(blank=True, null=True)
    cchalf_low = models.FloatField(blank=True, null=True)
    cchalf_overall = models.FloatField(blank=True, null=True)
    completeness_high = models.FloatField(blank=True, null=True)
    completeness_low = models.FloatField(blank=True, null=True)
    completeness_overall = models.FloatField(blank=True, null=True)
    crystal_name = models.ForeignKey(Crystal, on_delete=models.CASCADE, unique=True)  # changed to foreign key
    dimple_mtz_path = models.TextField(blank=True, null=True)
    dimple_pdb_path = models.TextField(blank=True, null=True)
    dimple_status = models.TextField(blank=True, null=True)
    image_path = models.TextField(blank=True, null=True)
    isig_high = models.FloatField(blank=True, null=True)
    isig_low = models.FloatField(blank=True, null=True)
    isig_overall = models.FloatField(blank=True, null=True)
    lattice = models.TextField(blank=True, null=True)
    log_name = models.TextField(blank=True, null=True)
    logfile_path = models.TextField(blank=True, null=True)
    mtz_name = models.TextField(blank=True, null=True)
    mtz_path = models.TextField(blank=True, null=True)
    multiplicity_high = models.FloatField(blank=True, null=True)
    multiplicity_low = models.FloatField(blank=True, null=True)
    multiplicity_overall = models.FloatField(blank=True, null=True)
    original_directory = models.TextField(blank=True, null=True)
    point_group = models.TextField(blank=True, null=True)
    program = models.TextField(blank=True, null=True)
    r_cryst = models.FloatField(blank=True, null=True)
    r_free = models.FloatField(blank=True, null=True)
    r_merge_high = models.FloatField(blank=True, null=True)
    r_merge_low = models.FloatField(blank=True, null=True)
    r_merge_overall = models.FloatField(blank=True, null=True)
    res_high = models.FloatField(blank=True, null=True)
    res_high_15_sigma = models.FloatField(blank=True, null=True)
    res_high_outer_shell = models.FloatField(blank=True, null=True)
    res_low = models.FloatField(blank=True, null=True)
    res_low_inner_shell = models.FloatField(blank=True, null=True)
    res_overall = models.TextField(blank=True, null=True)  # range
    score = models.FloatField(blank=True, null=True)
    spacegroup = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    unique_ref_overall = models.IntegerField(blank=True, null=True)
    unit_cell = models.TextField(blank=True, null=True)
    unit_cell_vol = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'data_processing'


class Dimple(models.Model):
    crystal_name = models.ForeignKey(Crystal, on_delete=models.CASCADE, unique=True)  # changed to foreign key
    mtz_path = models.CharField(max_length=255, blank=True, null=True)
    pdb_path = models.CharField(max_length=255, blank=True, null=True)
    r_free = models.FloatField(blank=True, null=True)
    res_high = models.FloatField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    reference = models.ForeignKey(
        Reference, blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'dimple'
        unique_together = ('pdb_path', 'mtz_path')

class Lab(models.Model):
    cryo_frac = models.FloatField(blank=True, null=True)
    cryo_status = models.TextField(blank=True, null=True)
    cryo_stock_frac = models.FloatField(blank=True, null=True)
    cryo_transfer_vol = models.FloatField(blank=True, null=True)
    crystal_name = models.ForeignKey(Crystal, on_delete=models.CASCADE, unique=True)  # changed to foreign key
    data_collection_visit = models.TextField(blank=True, null=True)
    expr_conc = models.FloatField(blank=True, null=True)
    harvest_status = models.TextField(blank=True, null=True)
    library_name = models.TextField(blank=True, null=True)
    library_plate = models.TextField(blank=True, null=True)
    mounting_result = models.TextField(blank=True, null=True)
    mounting_time = models.TextField(blank=True, null=True)
    soak_status = models.TextField(blank=True, null=True)
    soak_time = models.TextField(blank=True, null=True)
    soak_vol = models.FloatField(blank=True, null=True)
    solv_frac = models.FloatField(blank=True, null=True)
    stock_conc = models.FloatField(blank=True, null=True)
    visit = models.TextField(blank=True, null=True)
    # added - can be ignored anyway
    puck = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    pin_barcode = models.CharField(max_length=100, blank=True, null=True)
    arrival_time = models.DateTimeField(blank=True, null=True)
    mounted_timestamp = models.DateTimeField(blank=True, null=True)
    ispyb_status = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'lab'


class Refinement(models.Model):
    bound_conf = models.CharField(
        max_length=255, blank=True, null=True, unique=True)
    cif = models.TextField(blank=True, null=True)
    cif_prog = models.TextField(blank=True, null=True)
    cif_status = models.TextField(blank=True, null=True)
    crystal_name = models.ForeignKey(Crystal, on_delete=models.CASCADE, unique=True)  # changed to foreign key
    lig_bound_conf = models.TextField(blank=True, null=True)
    lig_cc = models.TextField(blank=True, null=True)
    lig_confidence = models.TextField(blank=True, null=True)
    lig_confidence_int = models.IntegerField(blank=True, null=True)
    lig_confidence_string = models.TextField(blank=True, null=True)
    matrix_weight = models.TextField(blank=True, null=True)
    molprobity_score = models.FloatField(blank=True, null=True)
    mtz_free = models.TextField(blank=True, null=True)
    mtz_latest = models.TextField(blank=True, null=True)
    outcome = models.IntegerField(blank=True, null=True)
    pdb_latest = models.TextField(blank=True, null=True)
    r_free = models.FloatField(blank=True, null=True)
    ramachandran_favoured = models.TextField(blank=True, null=True)
    ramachandran_outliers = models.TextField(blank=True, null=True)
    rcryst = models.FloatField(blank=True, null=True)
    refinement_path = models.TextField(blank=True, null=True)
    res = models.FloatField(blank=True, null=True)
    rmsd_angles = models.TextField(blank=True, null=True)
    rmsd_bonds = models.TextField(blank=True, null=True)
    spacegroup = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'refinement'


class PanddaAnalysis(models.Model):
    pandda_dir = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'pandda_analysis'


class PanddaRun(models.Model):
    input_dir = models.TextField(blank=True, null=True)
    pandda_analysis = models.ForeignKey(
        PanddaAnalysis, on_delete=models.CASCADE)
    pandda_log = models.CharField(max_length=255, unique=True)
    pandda_version = models.TextField(blank=True, null=True)
    sites_file = models.TextField(blank=True, null=True)
    events_file = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'pandda_run'


class PanddaStatisticalMap(models.Model):
    resolution_from = models.FloatField(blank=True, null=True)
    resolution_to = models.FloatField(blank=True, null=True)
    dataset_list = models.TextField()
    pandda_run = models.ForeignKey(PanddaRun, on_delete=models.CASCADE)

    class Meta:
        db_table = 'pandda_statistical_map'
        unique_together = ('resolution_from', 'resolution_to', 'pandda_run')


class PanddaSite(models.Model):
    pandda_run = models.ForeignKey(PanddaRun, on_delete=models.CASCADE)
    site = models.IntegerField(blank=True, null=True, db_index=True)
    site_aligned_centroid_x = models.FloatField(blank=True, null=True)
    site_aligned_centroid_y = models.FloatField(blank=True, null=True)
    site_aligned_centroid_z = models.FloatField(blank=True, null=True)
    site_native_centroid_x = models.FloatField(blank=True, null=True)
    site_native_centroid_y = models.FloatField(blank=True, null=True)
    site_native_centroid_z = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'pandda_site'
        unique_together = ('pandda_run', 'site')


class PanddaEvent(models.Model):
    crystal = models.ForeignKey(Crystal, on_delete=models.CASCADE)
    site = models.ForeignKey(PanddaSite, on_delete=models.CASCADE)
    refinement = models.ForeignKey(Refinement, on_delete=models.CASCADE)
    data_proc = models.ForeignKey(DataProcessing, on_delete=models.CASCADE)
    pandda_run = models.ForeignKey(PanddaRun, on_delete=models.CASCADE)
    event = models.IntegerField(blank=True, null=True, db_index=True)
    event_centroid_x = models.FloatField(blank=True, null=True)
    event_centroid_y = models.FloatField(blank=True, null=True)
    event_centroid_z = models.FloatField(blank=True, null=True)
    event_dist_from_site_centroid = models.TextField(blank=True, null=True)
    lig_centroid_x = models.FloatField(blank=True, null=True)
    lig_centroid_y = models.FloatField(blank=True, null=True)
    lig_centroid_z = models.FloatField(blank=True, null=True)
    lig_dist_event = models.FloatField(blank=True, null=True)
    lig_id = models.TextField(blank=True, null=True)
    pandda_event_map_native = models.TextField(blank=True, null=True)
    pandda_event_map_cut = models.TextField(blank=True, null=True)
    pandda_model_pdb = models.TextField(blank=True, null=True)
    pandda_input_mtz = models.TextField(blank=True, null=True)
    pandda_input_pdb = models.TextField(blank=True, null=True)
    ligand_confidence_inspect = models.TextField(blank=True, null=True)
    ligand_confidence = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    interesting = models.BooleanField()
    event_status = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, null=True)

    # model types
    NONE = 'NA'
    SOAKDB = 'SD'
    FRAGSPECT = 'FS'

    CHOICES = (
        (NONE, 'none'),
        (SOAKDB, 'soak_db'),
        (FRAGSPECT, 'fragspect')
    )

    ligand_confidence_source = models.CharField(
        choices=CHOICES, max_length=2, default=NONE)

    class Meta:
        db_table = 'pandda_event'
        unique_together = ('site', 'event', 'crystal', 'pandda_run')


class PanddaEventStats(models.Model):
    event = models.ForeignKey(PanddaEvent, on_delete=models.CASCADE)
    one_minus_bdc = models.FloatField(blank=True, null=True)
    cluster_size = models.IntegerField(blank=True, null=True)
    glob_corr_av_map = models.FloatField(blank=True, null=True)
    glob_corr_mean_map = models.FloatField(blank=True, null=True)
    loc_corr_av_map = models.FloatField(blank=True, null=True)
    loc_corr_mean_map = models.FloatField(blank=True, null=True)
    z_mean = models.FloatField(blank=True, null=True)
    z_peak = models.FloatField(blank=True, null=True)
    b_factor_scaled = models.FloatField(blank=True, null=True)
    high_res = models.FloatField(blank=True, null=True)
    low_res = models.FloatField(blank=True, null=True)
    r_free = models.FloatField(blank=True, null=True)
    r_work = models.FloatField(blank=True, null=True)
    ref_rmsd = models.FloatField(blank=True, null=True)
    wilson_scaled_b = models.FloatField(blank=True, null=True)
    wilson_scaled_ln_dev = models.FloatField(blank=True, null=True)
    wilson_scaled_ln_dev_z = models.FloatField(blank=True, null=True)
    wilson_scaled_ln_rmsd = models.FloatField(blank=True, null=True)
    wilson_scaled_ln_rmsd_z = models.FloatField(blank=True, null=True)
    wilson_scaled_below_four_rmsd = models.FloatField(blank=True, null=True)
    wilson_scaled_below_four_rmsd_z = models.FloatField(blank=True, null=True)
    wilson_scaled_above_four_rmsd = models.FloatField(blank=True, null=True)
    wilson_scaled_above_four_rmsd_z = models.FloatField(blank=True, null=True)
    wilson_scaled_rmsd_all = models.FloatField(blank=True, null=True)
    wilson_scaled_rmsd_all_z = models.FloatField(blank=True, null=True)
    wilson_unscaled = models.FloatField(blank=True, null=True)
    wilson_unscaled_ln_dev = models.FloatField(blank=True, null=True)
    wilson_unscaled_ln_dev_z = models.FloatField(blank=True, null=True)
    wilson_unscaled_ln_rmsd = models.FloatField(blank=True, null=True)
    wilson_unscaled_ln_rmsd_z = models.FloatField(blank=True, null=True)
    wilson_unscaled_below_four_rmsd = models.FloatField(blank=True, null=True)
    wilson_unscaled_below_four_rmsd_z = models.FloatField(
        blank=True, null=True)
    wilson_unscaled_above_four_rmsd = models.FloatField(blank=True, null=True)
    wilson_unscaled_above_four_rmsd_z = models.FloatField(
        blank=True, null=True)
    wilson_unscaled_rmsd_all = models.FloatField(blank=True, null=True)
    wilson_unscaled_rmsd_all_z = models.FloatField(blank=True, null=True)
    resolution = models.FloatField(blank=True, null=True)
    map_uncertainty = models.FloatField(blank=True, null=True)
    obs_map_mean = models.FloatField(blank=True, null=True)
    obs_map_rms = models.FloatField(blank=True, null=True)
    z_map_kurt = models.FloatField(blank=True, null=True)
    z_map_mean = models.FloatField(blank=True, null=True)
    z_map_skew = models.FloatField(blank=True, null=True)
    z_map_std = models.FloatField(blank=True, null=True)
    scl_map_mean = models.FloatField(blank=True, null=True)
    scl_map_rms = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'pandda_event_stats'


class MiscFiles(models.Model):
    file = models.FileField(max_length=500)
    description = models.TextField()

    class Meta:
        db_table = 'misc_files'



class FragalysisTarget(models.Model):
    target = models.CharField(max_length=255)
    metadata_file = models.FileField(blank=True, max_length=500)
    input_root = models.TextField()
    staging_root = models.TextField()
    reference = models.FileField(blank=True, max_length=500) # Should this be a crystal_fk or a text field with the name of the file in it...
    biomol = models.FileField(blank=True, max_length=500)
    additional_files = models.ManyToManyField(MiscFiles)

    class Meta:
        db_table = 'fragalysis_target'


class FragalysisLigand(models.Model):
    ligand_name = models.CharField(max_length=255)
    fragalysis_target = models.ForeignKey(
        FragalysisTarget, on_delete=models.CASCADE)
    crystallographic_bound = models.FileField(max_length=500)
    lig_mol_file = models.FileField(max_length=500)
    apo_pdb = models.FileField(max_length=500)
    bound_pdb = models.FileField(max_length=500)
    smiles_file = models.FileField(max_length=500)
    desolvated_pdb = models.FileField(max_length=500)
    solvated_pdb = models.FileField(max_length=500)
    pandda_event = models.FileField(blank=True, max_length=500)
    two_fofc = models.FileField(blank=True, max_length=500)
    fofc = models.FileField(blank=True, max_length=500)
    modification_date = models.BigIntegerField(blank=False, null=False)

    class Meta:
        db_table = 'fragalysis_ligand'


class Ligand(models.Model):
    fragalysis_ligand = models.ForeignKey(
        FragalysisLigand, on_delete=models.CASCADE)
    crystal = models.ForeignKey(Crystal, on_delete=models.CASCADE)
    target = models.ForeignKey(Target, on_delete=models.CASCADE)
    #compound = models.ForeignKey(Compounds, on_delete=models.CASCADE)

    class Meta:
        db_table = 'ligand'

class ReviewResponses(models.Model):
    # This may not be correctly linked in psql...
    crystal = models.ForeignKey(Crystal, on_delete=models.CASCADE)
    # may need to be changed to ligand in the end. Depends on XCR
    ligand_name = models.ForeignKey(Ligand, on_delete=models.CASCADE)
    fedid = models.TextField(blank=False, null=False)
    decision_int = models.IntegerField(blank=False, null=False)
    decision_str = models.TextField(blank=False, null=False)
    reason = models.TextField(blank=False, null=False)
    time_submitted = models.IntegerField(blank=False, null=False)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'review_responses'

class BadAtoms(models.Model):
    #review = models.ForeignKey(ReviewResponses, on_delete=models.CASCADE) # Removing review attachment - now solely limited to the Ligands (not fragalysis ligands)?
    ligand = models.ForeignKey(Ligand, on_delete=models.CASCADE)
    atomid = models.TextField(blank=False, null=False) # Will be now stored as a plain "0;1;2;3" string instead of each atom being an individual row.
    comment = models.TextField(blank=False, null=False) # Same thing as above
    atomname = models.TextField(blank=True, null=False) # Same thing as above

    class Meta:
        db_table = 'bad_atoms'


class MetaData(models.Model):
    ligand_name = models.ForeignKey(FragalysisLigand, on_delete=models.CASCADE)
    site_Label = models.CharField(blank=False, null=False, max_length=255)
    new_smiles = models.TextField(blank=True)
    alternate_name = models.CharField(max_length=255, blank=True)
    pdb_id = models.CharField(max_length=255, blank=True)
    fragalysis_name = models.CharField(max_length=255, unique=True)
    original_name = models.CharField(max_length=255)
    status = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'meta_data'


class ProteinSite(models.Model):
    fragalysis_ligand_reference = models.ForeignKey(FragalysisLigand, on_delete=models.CASCADE)  # Crystal to be aligned to
    site_name = models.CharField(max_length=50, blank=False, null=False)
    site_chain = models.CharField(max_length=50, blank=False, null=False)
    site_conformation = models.CharField(max_length=50, blank=False, null=False)
    site_crystal_form = models.CharField(max_length=50, blank=False, null=False)
    site_residue_names = ListTextField(base_field=models.CharField(max_length=255, blank=False, null=False), blank=False, null=False)
    site_residue_indicies = ListTextField(base_field=models.IntegerField(blank=False, null=False),blank=False, null=False)
    # Not sure we really need it but might be useful.
    creator = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'protein_sites'


class SiteMapping(models.Model):
    site = models.ForeignKey(ProteinSite, on_delete=models.CASCADE)  # The site
    # The ligand which belongs in this site
    ligand = models.ForeignKey(FragalysisLigand, on_delete=models.CASCADE)

    class Meta:
        db_table = 'site_mapping'

