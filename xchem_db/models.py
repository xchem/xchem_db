from __future__ import unicode_literals
from django.db import models

#INVENTORY DATA

class Protein(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    space_group = models.CharField(max_length=100, null=True, blank=True)
    a = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    b = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    c = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    alpha = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    beta = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    gamma = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)

#modified from original xchem_db model: added code attribute, smiles no longer unique, moved
class Compounds(models.Model):
    smiles = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=32, blank=True, null=True)

    log_p = models.FloatField(blank=True, null=True)
    mol_wt = models.FloatField(blank=True, null=True)
    heavy_atom_count = models.IntegerField(blank=True, null=True)
    heavy_atom_mol_wt = models.FloatField(blank=True, null=True)
    nhoh_count = models.IntegerField(blank=True, null=True)
    no_count = models.IntegerField(blank=True, null=True)
    num_h_acceptors = models.IntegerField(blank=True, null=True)
    num_h_donors = models.IntegerField(blank=True, null=True)
    num_het_atoms = models.IntegerField(blank=True, null=True)
    num_rot_bonds = models.IntegerField(blank=True, null=True)
    num_val_electrons = models.IntegerField(blank=True, null=True)
    ring_count = models.IntegerField(blank=True, null=True)
    tpsa = models.FloatField(blank=True, null=True)
    
    def __str__ (self):
        return self.code

class Library(models.Model):
    '''Compound library. If public=True, it is an XChem in-house library, otherwise
    it is brought in by the user'''

    name = models.CharField(max_length=100, blank=True, null=True)
    for_industry = models.BooleanField(default=False)
    public = models.BooleanField(default=False)

    def __str__ (self):
        return self.name

class LibraryPlate(models.Model):
    '''A library plate. last_tested is either the date of adding the plate
    to the database, or the last dispense test performed on it'''
		
    barcode = models.CharField(max_length=100, blank=True, null=True) #string to identify physical plate
    library = models.ForeignKey(Library, on_delete=models.PROTECT, related_name="plates" )
    current = models.BooleanField(default=True)
    last_tested =  models.DateField(auto_now=True)
    unique_together = ['barcode', 'library']

    def size(self):
        return len(self.compounds.all())

    def __str__ (self):
        return f"[{self.id}]{self.library}, {self.name}"

class SourceWell(models.Model):
    '''location of a particular compound in a particular library plate; concentration not always available'''

    compound = models.ForeignKey(Compounds, blank=True, null=True, on_delete=models.CASCADE, related_name="locations")
    library_plate =  models.ForeignKey(LibraryPlate, blank=True, null=True, on_delete=models.CASCADE, related_name="compounds")
    well  = models.CharField(max_length=4, blank=True, null=True)
    concentration = models.IntegerField(null=True, blank=True)
    active = models.BooleanField(default=True)   
    deactivation_date = models.DateField(blank=True, null=True)

    def __str__ (self):
        return f"{self.library_plate}: {self.well}"

class LibrarySubset(models.Model):
    '''A selection of compounds from a specific library; always created automatically
    Origin is an automatically generated string to inform how the subset was added to a selection.
    (e.g. if it belongs to a preset, or was uploaded by a user) '''

    name = models.CharField(max_length=100, blank=True, null=True)
    library = models.ForeignKey(Library, blank=True, null=True, on_delete=models.CASCADE)
    compounds = models.ManyToManyField(Compounds, blank=True)
    origin = models.CharField(max_length=64, blank=True, null=True)
    
    def __str__ (self):
        return f"{self.id}: {self.name} - {self.library.name}"
    
    def size(self):
        return len(self.compounds.all())

class Preset(models.Model):
    '''A selection of compounds created by the XChem staff for a specific purpose from one
    or more libraries (i.g. a selection of subsets with some metadata describing it)'''
    name = models.CharField(max_length=64, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    subsets = models.ManyToManyField(LibrarySubset, blank=True)

#EXPERIMENTAL DATA: old xchem_db models and new addition 


class Tasks(models.Model):
    task_name = models.CharField(max_length=255, blank=False, null=False, unique=False, db_index=True)
    uuid = models.CharField(max_length=37, blank=False, null=False, unique=True, db_index=True)

    class Meta:
        unique_together = ('task_name', 'uuid')

class Target(models.Model):

    target_name = models.CharField(max_length=255, blank=False, null=False, unique=True, db_index=True)
    # uniprot_id = models.CharField(blank=True, null=True)
    # alias = models.CharField(blank=True, null=True)

    class Meta:
        db_table = 'target'

class Reference(models.Model):
    reference_pdb = models.CharField(max_length=255, null=True, default='not_assigned', unique=True)

class Proposals(models.Model):

    # TODO - can we refactor this for title [original comment]
    proposal = models.CharField(max_length=255, blank=False, null=False, unique=True)
    title = models.CharField(max_length=10, blank=True, null=True)
    fedids = models.TextField(blank=True, null=True)

    #SPA-related data
    industry_user = models.BooleanField(default=True) # just in case false by default - fewer privileges
    protein = models.OneToOneField(Protein, blank=True, null=True, on_delete=models.PROTECT)
    libraries = models.ManyToManyField(Library, blank=True)
    subsets = models.ManyToManyField(LibrarySubset, blank=True)

    def __str__(self):
         return self.name + "proposal object"
         

class Visit(models.Model):
	visit_name = models.CharField(max_length=32, blank=True, null=True)
	proposal = models.ForeignKey(Proposals, on_delete=models.CASCADE)
	


class SoakdbFiles(models.Model):
    filename = models.CharField(max_length=255, blank=False, null=False, unique=True)
    modification_date = models.BigIntegerField(blank=False, null=False)
    proposal = models.ForeignKey(Proposals, on_delete=models.CASCADE, unique=False)
    visit = models.TextField(blank=False, null=False)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'soakdb_files'

#new class (SPA experimental data)	
class CrystalPlate(models.Model):
    name = models.CharField(max_length=100, default="new_plate")
    drop_volume = models.FloatField(blank=True, null=True)
    plate_type = models.CharField(max_length=50, blank=True, null=True)


#new class (SPA experimental data)	
class SpaCompound(models.Model):
    '''Compound data copied from inventory data when the compound is used
    in the experiment'''

    visit = models.ForeignKey(Visit, blank=True, null=True, on_delete=models.CASCADE)
    library_name = models.CharField(max_length=100)
    library_plate = models.CharField(max_length=100)
    well = models.CharField(max_length=4)
    code = models.CharField(max_length=100)
    smiles = models.CharField(max_length=256)
#    crystal = models.ForeignKey(Crystal, related_name="compounds", on_delete=models.PROTECT, blank=True, null=True) #to allow cocktails

#modified: added more attributes    
class Crystal(models.Model):

    crystal_name = models.CharField(max_length=255, blank=True, null=True, db_index=True) # changed to allow null: a crystal enters database before it is assigned name
    target = models.ForeignKey(Target, blank=True, null=True, on_delete=models.CASCADE)
    #compound = models.ForeignKey(Compounds, on_delete=models.CASCADE, null=True, blank=True) # Compounds is now an inventory model, not used directly in an experiment
    #visit = models.ForeignKey(SoakdbFiles, blank=True, null=True, on_delete=models.CASCADE) # blank/null temporarily added <---- old
    soakdb_file = models.ForeignKey(SoakdbFiles, blank=True, null=True, on_delete=models.CASCADE) # replaces old 'visit' field
    visit = models.ForeignKey(Visit, blank=True, null=True, on_delete=models.CASCADE) # new 'visit' field for experiments made without SoakDB
    
    product = models.CharField(max_length=255, blank=True, null=True)

    # model types
    PREPROCESSING = 'PP'
    PANDDA = 'PD'
    PROASIS = 'PR'
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

    status = models.CharField(choices=CHOICES, max_length=2, default=PREPROCESSING)

    #added SPA attributes
    crystal_plate = models.ForeignKey(CrystalPlate, blank=True, null=True, on_delete=models.PROTECT)
    well = models.CharField(max_length=4,  blank=True, null=True)
    echo_x = models.IntegerField(blank=True, null=True) #double-check if it shouldn't be float
    echo_y = models.IntegerField(blank=True, null=True) #double-check if it shouldn't be float
    score = models.IntegerField(blank=True, null=True)

    class Meta:
#        unique_together = ('crystal_name', 'visit', 'compound', 'product') <-- old
        unique_together = ('crystal_name', 'visit', 'product') #removed compound from unique_together to allow for cocktails


class CompoundCombination(models.Model):
	'''for combisoaks and cocktails'''
	visit = models.ForeignKey(Visit, blank=True, null=True, on_delete=models.PROTECT)
	number = models.IntegerField(blank=True, null=True)
	compounds = models.ManyToManyField(SpaCompound)
	related_crystals = models.CharField(max_length=64, null=True, blank=True)
	'''if a combination is based on the result of the previous soak,
	the crystals based on which the combination is created are recorder
	as related_crystals'''


#new class
class SolventNotes(models.Model):
    '''To store user's notes on conclusions from solvent testing; values
    not to be processed any further except for reminding the user to 
    apply cryo'''
    
    proposal = models.ForeignKey(Proposals, on_delete=models.CASCADE)
    solvent = models.CharField(max_length=32, blank=True, null=True)
    solvent_concentration = models.FloatField(blank=True, null=True)
    soak_time = models.DurationField(blank=True, null=True)
    cryo = models.CharField(max_length=32, blank=True, null=True)
    cryo_concentration = models.FloatField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

class SoakAndCryoValues(models.Model):
    '''abstract class created to manage differences between solvent testing and a screen with compounds;
    in a regular screen these values are the same for the whole batch, but in solvent characterisation
    experiments they are individual to each crystal'''    
    crystal_plate = models.ForeignKey(CrystalPlate, blank=True, null=True, on_delete=models.CASCADE)
    solv_frac = models.FloatField(blank=True, null=True)
    stock_conc = models.FloatField(blank=True, null=True)
    cryo_frac = models.FloatField(blank=True, null=True)
    cryo_stock_frac = models.FloatField(blank=True, null=True)
    cryo_location = models.CharField(max_length=4, blank=True, null=True)

    soak_vol = models.FloatField(blank=True, null=True)
    expr_conc = models.FloatField(blank=True, null=True) #compound concentration - can we rename?
    cryo_transfer_vol = models.FloatField(blank=True, null=True)

    class Meta:
        abstract = True

class SolventBatch(models.Model):
    '''data common to the whole batch of crystals in a solvent testing experiment'''    
    number = models.IntegerField(default=0)
    soak_status = models.CharField(max_length=64, blank=True, null=True)
    soak_time = models.IntegerField(blank=True, null=True)
    cryo_status = models.CharField(max_length=64, blank=True, null=True)
    
    def batch_name(self):
        return 'Batch-' + self.number + '_' + self.crystal_plate.name #needs verification

#new class (SPA experimental data)	
class Batch(SolventBatch, SoakAndCryoValues):
    '''A group of crystals that go through soaking and cryo together in a compound screen
    batch, soak and cryo the same for the whole batch in this kind of experiment'''
    pass

#new class (SPA experimental data)
class SolventTestingData(SoakAndCryoValues):
    '''solvent and cryo data for crystals used in solvent testing'''

    solvent_name = models.CharField(max_length=64, blank=True, null=True)
    batch = models.ForeignKey(SolventBatch, blank=True, null=True, on_delete=models.CASCADE)


class DataProcessing(models.Model):
    auto_assigned = models.TextField(blank=True, null=True)
    cchalf_high = models.FloatField(blank=True, null=True)
    cchalf_low = models.FloatField(blank=True, null=True)
    cchalf_overall = models.FloatField(blank=True, null=True)
    completeness_high = models.FloatField(blank=True, null=True)
    completeness_low = models.FloatField(blank=True, null=True)
    completeness_overall = models.FloatField(blank=True, null=True)
    crystal_name = models.OneToOneField(Crystal, on_delete=models.CASCADE, unique=True)  # changed to foreign key
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
    crystal_name = models.OneToOneField(Crystal, on_delete=models.CASCADE, unique=True)  # changed to foreign key
    mtz_path = models.CharField(max_length=255, blank=True, null=True)
    pdb_path = models.CharField(max_length=255, blank=True, null=True)
    r_free = models.FloatField(blank=True, null=True)
    res_high = models.FloatField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    reference = models.ForeignKey(Reference, blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('pdb_path', 'mtz_path')

#heavily modified; some attributes added, some moved to Batch
class Lab(models.Model):

    crystal_name = models.OneToOneField(Crystal, on_delete=models.CASCADE, unique=True, blank=True, null=True)  # changed to foreign key
    single_compound = models.ForeignKey(SpaCompound, on_delete=models.CASCADE, null=True, blank=True) # in regular experiments
    compound_combination = models.ForeignKey(CompoundCombination, on_delete=models.CASCADE, null=True, blank=True) # with combisoaks and cocktails

    #compound = models.OneToOneField(SpaCompound, on_delete=models.CASCADE, unique=True, blank=True, null=True)  #changed to allow cocktails
    #to access crystal_name now: self.compound.crystal
        
    data_collection_visit = models.CharField(max_length=64, blank=True, null=True)
    harvest_status = models.CharField(max_length=64, blank=True, null=True)
    mounting_result = models.CharField(max_length=64, blank=True, null=True)
    mounting_time = models.CharField(max_length=64, blank=True, null=True)
    visit = models.CharField(max_length=64, blank=True, null=True)

    #new attributes
    batch = models.ForeignKey(Batch, blank=True, null=True, on_delete=models.PROTECT) #null for solvent testing
    solvent_data = models.ForeignKey(SolventTestingData, blank=True, null=True, on_delete=models.PROTECT) #null for compound screen
    puck = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    pin_barcode = models.CharField(max_length=100, blank=True, null=True)
    arrival_time = models.DateTimeField(blank=True, null=True)
    mounted_timestamp = models.DateTimeField(blank=True, null=True)
    ispyb_status = models.CharField(max_length=100, blank=True, null=True)

'''
#(requires installing json field:
#pip install jsonfield)
from jsonfield import JSONField

class SolventAutofill(models.Model):
    #patterns of typical parameters used in solvent testing; used for auto-filling data
    
    name = models.CharField(max_length=100)
    solvents = JSONField() #array of strings
    solvent_concentrations = JSONField() #array of floats
    cryo = models.BooleanField()
    comment = models.textField()
'''


#ONLY OLD UNCHANGED MODELS BELOW

class Refinement(models.Model):
    bound_conf = models.CharField(max_length=255, blank=True, null=True, unique=True)
    cif = models.TextField(blank=True, null=True)
    cif_prog = models.TextField(blank=True, null=True)
    cif_status = models.TextField(blank=True, null=True)
    crystal_name = models.OneToOneField(Crystal, on_delete=models.CASCADE, unique=True)  # changed to foreign key
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

class PanddaAnalysis(models.Model):
    pandda_dir = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'pandda_analysis'


class PanddaRun(models.Model):
    input_dir = models.TextField(blank=True, null=True)
    pandda_analysis = models.ForeignKey(PanddaAnalysis, on_delete=models.CASCADE)
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

    ligand_confidence_source = models.CharField(choices=CHOICES, max_length=2, default=NONE)

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
    wilson_unscaled_below_four_rmsd_z = models.FloatField(blank=True, null=True)
    wilson_unscaled_above_four_rmsd = models.FloatField(blank=True, null=True)
    wilson_unscaled_above_four_rmsd_z = models.FloatField(blank=True, null=True)
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
        db_table = 'MiscFiles'


class FragalysisTarget(models.Model):
    open = models.BooleanField()
    target = models.CharField(max_length=255)
    metadata_file = models.FileField(blank=True, max_length=500)
    input_root = models.TextField()
    staging_root = models.TextField()
    biomol = models.FileField(blank=True, max_length=500)
    additional_files = models.ManyToManyField(MiscFiles)

    class Meta:
        db_table = 'FragalysisTarget'


class FragalysisLigand(models.Model):
    ligand_name = models.CharField(max_length=255)
    fragalysis_target = models.ForeignKey(FragalysisTarget, on_delete=models.CASCADE)
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
        db_table = 'FragalysisLigand'


class Ligand(models.Model):
    fragalysis_ligand = models.ForeignKey(FragalysisLigand, on_delete=models.CASCADE)
    crystal = models.ForeignKey(Crystal, on_delete=models.CASCADE)
    target = models.ForeignKey(Target, on_delete=models.CASCADE)
    compound = models.ForeignKey(Compounds, on_delete=models.CASCADE)

# Old Review
class ReviewResponses(models.Model):
    crystal = models.ForeignKey(Crystal, on_delete=models.CASCADE)  # This may not be correctly linked in psql...
    # may need to be changed to ligand in the end. Depends on XCR
    # Ligand_name = models.ForeignKey(Ligand)
    fedid = models.TextField(blank=False, null=False)
    decision_int = models.IntegerField(blank=False, null=False)
    decision_str = models.TextField(blank=False, null=False)
    reason = models.TextField(blank=False, null=False)
    time_submitted = models.IntegerField(blank=False, null=False)

    class Meta:
        db_table = 'review_responses'


# New Class as the old one is STILL IN USE!
class ReviewResponses2(models.Model):
    crystal = models.ForeignKey(Crystal, on_delete=models.CASCADE)  # This may not be correctly linked in psql...
    # may need to be changed to ligand in the end. Depends on XCR
    Ligand_name = models.ForeignKey(Ligand, on_delete=models.CASCADE)
    fedid = models.TextField(blank=False, null=False)
    decision_int = models.IntegerField(blank=False, null=False)
    decision_str = models.TextField(blank=False, null=False)
    reason = models.TextField(blank=False, null=False)
    time_submitted = models.IntegerField(blank=False, null=False)

    class Meta:
        db_table = 'review_responses_new'


class BadAtoms(models.Model):
    Review = models.ForeignKey(ReviewResponses2, on_delete=models.CASCADE)
    Ligand = models.ForeignKey(Ligand, on_delete=models.CASCADE)
    atomid = models.IntegerField(blank=False, null=False)
    comment = models.TextField(blank=False, null=False)

    class Meta:
        db_table = 'bad_atoms'


class MetaData(models.Model):
    Ligand_name = models.ForeignKey(FragalysisLigand, on_delete=models.CASCADE)
    Site_Label = models.CharField(blank=False, null=False, max_length=255)
    new_smiles = models.TextField(blank=True)
    alternate_name = models.CharField(max_length=255, blank=True)
    pdb_id = models.CharField(max_length=255, blank=True)
    fragalysis_name = models.CharField(max_length=255, unique=True)
    original_name = models.CharField(max_length=255)
