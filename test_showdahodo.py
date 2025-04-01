from plotbot.custom_variables import custom_variable
from plotbot.showdahodo import showdahodo
from plotbot.test_pilot import phase, system_check
from plotbot.print_manager import print_manager

@pytest.mark.mission("Single Custom Variable in Showdahodo")
def test_single_custom_variable(test_environment):
    """Test using a single custom variable in showdahodo"""
    
    print("\n================================================================================")
    print("TEST #3: Single Custom Variable in Showdahodo")
    print("Verifies that showdahodo works with one custom variable")
    print("================================================================================\n")
    
    # Get the time range from the fixture
    trange = test_environment
    
    phase(1, "Creating custom variable")
    # Create TAoverB custom variable
    ta_over_b = custom_variable('TAoverB', proton.anisotropy / mag_rtn_4sa.bmag)
    
    # Set some properties
    ta_over_b.y_label = "Temperature Anisotropy / |B|"
    ta_over_b.legend_label = "TA/|B|"
    
    # Print some diagnostics
    print_manager.test(f"Custom variable data_type: {ta_over_b.data_type}")
    print_manager.test(f"Custom variable class_name: {ta_over_b.class_name}")
    
    phase(2, "Creating hodogram with custom variable as x-axis")
    # Create hodogram with custom variable
    fig1, ax1 = showdahodo(trange, ta_over_b, mag_rtn_4sa.br)

@pytest.mark.mission("Dual Custom Variables in Showdahodo")
def test_dual_custom_variables(test_environment):
    """Test using two custom variables in showdahodo"""
    
    print("\n================================================================================")
    print("TEST #4: Dual Custom Variables in Showdahodo")
    print("Verifies that showdahodo works with two custom variables")
    print("================================================================================\n")
    
    # Get the time range from the fixture
    trange = test_environment
    
    phase(1, "Creating two custom variables")
    # Create first custom variable
    ta_over_b = custom_variable('TAoverB', proton.anisotropy / mag_rtn_4sa.bmag)
    ta_over_b.legend_label = "TA/|B|"
    
    # Create second custom variable
    br_squared = custom_variable('BrSquared', mag_rtn_4sa.br * mag_rtn_4sa.br)
    br_squared.legend_label = "Br²" 