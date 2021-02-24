# This file includes new additional models to accomodate WebSoakDB, as
# well as modifications to the old models. Original comment below.

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
#  Feel free to rename the models, but don't rename db_table values or field names.


from __future__ import unicode_literals
from django.db import models
import os

#WebSoakDB addition:
from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem import Crippen

#INVENTORY DATA - mostly SoakDB-only classes

class Protein(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    space_group = models.CharField(max_length=100, null=True, blank=True)
    a = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    b = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    c = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    alpha = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    beta = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    gamma = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
	
    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'protein'

#modified from original xchem_db model: added code attribute, smiles no longer unique, moved
class Compounds(models.Model):
    smiles = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=32,  blank=True, null=True)
    
    def properties(self):
        sanitized_mol = Chem.MolFromSmiles(self.smiles)
		
        new_mol = {}
        new_mol['log_p'] = Crippen.MolLogP(sanitized_mol)
        new_mol['mol_wt'] = float(Chem.rdMolDescriptors.CalcExactMolWt(sanitized_mol))
        new_mol['heavy_atom_count'] = Chem.Lipinski.HeavyAtomCount(sanitized_mol)
        new_mol['heavy_atom_mol_wt'] = float(Descriptors.HeavyAtomMolWt(sanitized_mol))
        new_mol['nhoh_count'] = Chem.Lipinski.NHOHCount(sanitized_mol)
        new_mol['no_count'] = Chem.Lipinski.NOCount(sanitized_mol)
        new_mol['num_h_acceptors'] = Chem.Lipinski.NumHAcceptors(sanitized_mol)
        new_mol['num_h_donors'] = Chem.Lipinski.NumHDonors(sanitized_mol)
        new_mol['num_het_atoms'] = Chem.Lipinski.NumHeteroatoms(sanitized_mol)
        new_mol['num_rot_bonds'] = Chem.Lipinski.NumRotatableBonds(sanitized_mol)
        new_mol['num_val_electrons'] = Descriptors.NumValenceElectrons(sanitized_mol)
        new_mol['ring_count'] = Chem.Lipinski.RingCount(sanitized_mol)
        new_mol['tpsa'] = Chem.rdMolDescriptors.CalcTPSA(sanitized_mol)

        return new_mol
    
    def molecular_weight(self):
        return mol_wt(self.smiles)
    
    def tpsa(self):
        return tpsa(self.smiles)

    def __str__ (self):
        return self.code

    class Meta:
       if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
       db_table = 'compounds'

class Library(models.Model):
    '''Compound library. If public=True, it is an XChem in-house library, otherwise
    it is brought in by the user'''

    name = models.CharField(max_length=100)
    for_industry = models.BooleanField(default=False)
    public = models.BooleanField(default=False)

    def __str__ (self):
        return self.name
	
    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'library'

class LibraryPlate(models.Model):
    '''A library plate. last_tested is either the date of adding the plate
    to the database, or the last dispense test performed on it'''
		
    name = models.CharField(max_length=100)
    library = models.ForeignKey(Library, on_delete=models.PROTECT, related_name="plates" )
    current = models.BooleanField(default=True)
    last_tested =  models.DateField(auto_now=True)
    unique_together = ['name', 'library']

    def size(self):
        return len(self.compounds.all())

    def __str__ (self):
        return f"[{self.id}]{self.library}, {self.name}"
	
    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'library_plate'


class SourceWell(models.Model):
    '''location of a particular compound in a particular library plate; concentration not always available'''

    compound = models.ForeignKey(Compounds, on_delete=models.CASCADE, related_name="locations")
    library_plate =  models.ForeignKey(LibraryPlate, on_delete=models.CASCADE, related_name="compounds")
    well  = models.CharField(max_length=4)
    concentration = models.IntegerField(null=True, blank=True)

    def __str__ (self):
        return f"{self.library_plate}: {self.well}"
    
    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'source_well'


class LibrarySubset(models.Model):
    '''A selection of compounds from a specific library; always created automatically
    Origin is an automatically generated string to inform how the subset was added to a selection.
    (e.g. if it belongs to a preset, or was uploaded by a user) '''

    name = models.CharField(max_length=100)
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    compounds = models.ManyToManyField(Compounds, blank=True)
    origin = models.CharField(max_length=64)
    
    def __str__ (self):
        return f"{self.id}: {self.name} - {self.library.name}"
    
    def size(self):
        return len(self.compounds.all())
    
    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'library_subset'


class Preset(models.Model):
    '''A selection of compounds created by the XChem staff for a specific purpose from one
    or more libraries (i.g. a selection of subsets with some metadata describing it)'''
    name = models.CharField(max_length=64, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    subsets = models.ManyToManyField(LibrarySubset)
    
    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'preset'


#EXPERIMENTAL DATA: old xchem_db models and new addition 


class Tasks(models.Model):
    task_name = models.CharField(max_length=255, blank=False, null=False, unique=False, db_index=True)
    uuid = models.CharField(max_length=37, blank=False, null=False, unique=True, db_index=True)

    class Meta:
        app_label = 'xchem_db'
        db_table = 'tasks'
        unique_together = ('task_name', 'uuid')

class Target(models.Model):

    target_name = models.CharField(max_length=255, blank=False, null=False, unique=True, db_index=True)
    # uniprot_id = models.CharField(blank=True, null=True)
    # alias = models.CharField(blank=True, null=True)

    class Meta:
        app_label = 'xchem_db'
        db_table = 'target'

class Reference(models.Model):
    reference_pdb = models.CharField(max_length=255, null=True, default='not_assigned', unique=True)

    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
           app_label = 'xchem_db'
        db_table = 'reference'

#modified: 'proposal' changed to 'name', added SoakDB-related attributes and __str__
class Proposals(models.Model):

    # TODO - can we refactor this for title [original comment]
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    title = models.CharField(max_length=10, blank=True, null=True)
    fedids = models.TextField(blank=True, null=True)

    #SoakDB-related data
    industry_user = models.BooleanField(default=True) # just in case false by default - fewer privileges
    protein = models.OneToOneField(Protein, blank=True, null=True, on_delete=models.PROTECT)
    libraries = models.ManyToManyField(Library, blank=True)
    subsets = models.ManyToManyField(LibrarySubset, blank=True)

    def __str__(self):
         return self.name + "proposal object"

    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'proposals'


class SoakdbFiles(models.Model):
    filename = models.CharField(max_length=255, blank=False, null=False, unique=True)
    modification_date = models.BigIntegerField(blank=False, null=False)
    proposal = models.ForeignKey(Proposals, on_delete=models.CASCADE, unique=False)
    visit = models.TextField(blank=False, null=False)
    status = models.IntegerField(blank=True, null=True)


    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'soakdb_files'

#new class (SoakDB experimental data)	
class CrystalPlate(models.Model):
    name = models.CharField(max_length=100)
    drop_volume = models.FloatField()
    
    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'crystal_plate'

#modified: added more attributes    
class Crystal(models.Model):

    crystal_name = models.CharField(max_length=255, blank=True, null=True, db_index=True) # changed to allow null: a crystal enters database before it is assigned name
    target = models.ForeignKey(Target, blank=True, null=True, on_delete=models.CASCADE)
    #compound = models.ForeignKey(Compounds, on_delete=models.CASCADE, null=True, blank=True) removed to allow for cocktails
    visit = models.ForeignKey(SoakdbFiles, blank=True, null=True, on_delete=models.CASCADE) # blank/null temporarily added
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

    #added SoakDB attributes

    crystal_plate = models.ForeignKey(CrystalPlate, blank=True, null=True, on_delete=models.PROTECT) #need to do something about nullability
    well = models.CharField(max_length=4,  blank=True, null=True)
    echo_x = models.IntegerField(blank=True, null=True,) #double-check if it shouldn't be float
    echo_y = models.IntegerField(blank=True, null=True,) #double-check if it shouldn't be float
    score = models.IntegerField(blank=True, null=True,)
#    image -- need to figure out how this will be stored

    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'crystal'
#        unique_together = ('crystal_name', 'visit', 'compound', 'product')
        unique_together = ('crystal_name', 'visit', 'product') #removed compound from unique_together to allow for cocktails

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
    
    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'solvent_notes'


#new class (SoakDB experimental data)	
class SoakDBCompound(models.Model):
    '''Compound data copied from inventory data when the compound is used
    in the experiment'''

    proposal = models.ForeignKey(Proposals, related_name="exp_compounds", on_delete=models.CASCADE, blank=True, null=True)
    library_name = models.CharField(max_length=100)
    library_plate = models.CharField(max_length=100)
    well = models.CharField(max_length=4)
    code = models.CharField(max_length=100)
    smiles = models.CharField(max_length=256)
    crystal = models.ForeignKey(Crystal, related_name="compounds", on_delete=models.PROTECT, blank=True, null=True) #to allow cocktails
    
    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'soakdb_compound'

class SoakAndCryoValues(models.Model):
    '''abstract class to manage differences between solvent testing and a screen with compounds'''    
    crystal_plate = models.ForeignKey(CrystalPlate, blank=True, null=True, on_delete=models.CASCADE)
    solv_frac = models.FloatField(blank=True, null=True)
    stock_conc = models.FloatField(blank=True, null=True)
    cryo_frac = models.FloatField(blank=True, null=True)
    cryo_stock_frac = models.FloatField(blank=True, null=True)
    cryo_location = models.CharField(max_length=4, blank=True, null=True)

    #based on macros in the original SoakDB file; consulted with Ailsa
    def soak_vol(self): #supposing it means soak transfer volume -- needs verification
        min_vol_unit = 2.5
        volume = (self.crystal_plate.drop_volume * self.solv_frac) / (100 - self.solv_frac)
        return round(volume /min_vol_unit , 0) * min_vol_unit

    def compound_conc(self):
        concentration = (self.stock_conc * self.soak_vol())/(self.crystal_plate.drop_vol + self.soak_vol)
        return round(concentration, 1)

    def cryo_transfer_vol(self):
        min_vol_unit = 2.5
        volume = (self.cryo_frac * self.crystal_plate.drop_volume)/(self.stock_frac - self.cryo_frac)
        return round(volume /min_vol_unit, 0) * min_vol_unit
    
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
    
    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'solvent_batch'

#new class (SoakDB experimental data)	
class Batch(SolventBatch, SoakAndCryoValues):
    '''A group of crystals that go through soaking and cryo together in a compound screen
    batch, soak and cryo the same for the whole batch in this kind of experiment'''
    pass
    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'batch'

#new class (SoakDB experimental data)
class SolventTestingData(SoakAndCryoValues):
    '''solvent and cryo data for crystals used in solvent testing'''

    solvent_name = models.CharField(max_length=64, blank=True, null=True)
    batch = models.ForeignKey(SolventBatch, blank=True, null=True, on_delete=models.CASCADE)
    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'solvent_testing_data'


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
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
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
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'dimple'
        unique_together = ('pdb_path', 'mtz_path')

#heavily modified; some attributes added, some moved to Batch
class Lab(models.Model):

    #crystal_name = models.OneToOneField(Crystal, on_delete=models.CASCADE, unique=True)  # changed to foreign key
    compound = models.OneToOneField(SoakDBCompound, on_delete=models.CASCADE, unique=True)  #changed to allow cocktails
    #to access crystal_name now: self.compound.crystal
        
    data_collection_visit = models.CharField(max_length=64, blank=True, null=True)
    expr_conc = models.FloatField(blank=True, null=True)
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
    

    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'lab'

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

    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'refinement'


class PanddaAnalysis(models.Model):
    pandda_dir = models.CharField(max_length=255, unique=True)

    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'pandda_analysis'


class PanddaRun(models.Model):
    input_dir = models.TextField(blank=True, null=True)
    pandda_analysis = models.ForeignKey(PanddaAnalysis, on_delete=models.CASCADE)
    pandda_log = models.CharField(max_length=255, unique=True)
    pandda_version = models.TextField(blank=True, null=True)
    sites_file = models.TextField(blank=True, null=True)
    events_file = models.TextField(blank=True, null=True)

    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'pandda_run'


class PanddaStatisticalMap(models.Model):
    resolution_from = models.FloatField(blank=True, null=True)
    resolution_to = models.FloatField(blank=True, null=True)
    dataset_list = models.TextField()
    pandda_run = models.ForeignKey(PanddaRun, on_delete=models.CASCADE)

    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
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
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
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
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
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
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'pandda_event_stats'


class MiscFiles(models.Model):
    file = models.FileField(max_length=500)
    description = models.TextField()

    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
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
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
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
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'FragalysisLigand'


class Ligand(models.Model):
    fragalysis_ligand = models.ForeignKey(FragalysisLigand, on_delete=models.CASCADE)
    crystal = models.ForeignKey(Crystal, on_delete=models.CASCADE)
    target = models.ForeignKey(Target, on_delete=models.CASCADE)
    compound = models.ForeignKey(Compounds, on_delete=models.CASCADE)

    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'ligand'

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
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
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
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'review_responses_new'


class BadAtoms(models.Model):
    Review = models.ForeignKey(ReviewResponses2, on_delete=models.CASCADE)
    Ligand = models.ForeignKey(Ligand, on_delete=models.CASCADE)
    atomid = models.IntegerField(blank=False, null=False)
    comment = models.TextField(blank=False, null=False)

    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'bad_atoms'


class MetaData(models.Model):
    Ligand_name = models.ForeignKey(FragalysisLigand, on_delete=models.CASCADE)
    Site_Label = models.CharField(blank=False, null=False, max_length=255)
    new_smiles = models.TextField(blank=True)
    alternate_name = models.CharField(max_length=255, blank=True)
    pdb_id = models.CharField(max_length=255, blank=True)
    fragalysis_name = models.CharField(max_length=255, unique=True)
    original_name = models.CharField(max_length=255)

    class Meta:
        if os.getcwd() != '/dls/science/groups/i04-1/software/luigi_pipeline/pipelineDEV':
            app_label = 'xchem_db'
        db_table = 'metadata'
