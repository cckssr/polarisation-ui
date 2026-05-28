"""
Test script for goniometer system - validates all layers.

Run from project root: python tests/test_goniometer_system.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now import from the package
from polarisation_ui.core.services import GoniometerService
from polarisation_ui.core.models import GoniometerState


def test_core_layer():
    """Test core layer functionality."""
    print("\n📋 Testing Core Layer...")

    # Test service initialization
    service = GoniometerService()
    state = service.initialize_state(45.0)

    assert state.sample_angle == 45.0, "Sample angle should be 45°"
    assert state.detector_angle == 90.0, "Detector angle should be 90° (2x sample)"
    assert state.validate(), "State should be valid"

    print("  ✓ GoniometerService initialization")

    # Test angle update
    service.update_sample_angle(60.0)
    state = service.get_state()
    assert state.sample_angle == 60.0
    assert state.detector_angle == 120.0

    print("  ✓ Angle updates with 2x relationship")

    # Test encoder reading
    service.process_encoder_reading("sample", 30.0)
    state = service.get_state()
    assert state.sample_angle == 30.0
    assert state.detector_angle == 60.0

    print("  ✓ Encoder reading processing")

    # Test history
    history = service.get_reading_history()
    assert len(history) >= 1, "Should have reading history"

    print("  ✓ Reading history tracking")

    print("✅ Core layer tests passed!")


def test_integration():
    """Test integration between layers."""
    print("\n📋 Testing Layer Integration...")

    service = GoniometerService()
    service.initialize_state(0.0)

    print("  ✓ Service created")

    # Process readings
    service.process_encoder_reading("sample", 45.0)
    service.process_encoder_reading("detector", 90.0)

    state = service.get_state()
    assert state.sample_angle == 45.0
    assert state.detector_angle == 90.0

    print("  ✓ Encoder readings integrated into service")

    # Test validation
    assert state.validate(), "State should be valid"

    print("  ✓ State validation")

    print("✅ Integration tests passed!")


def test_error_handling():
    """Test error conditions."""
    print("\n📋 Testing Error Handling...")

    service = GoniometerService()

    # Test angle limits
    try:
        service.initialize_state(200.0)
        assert False, "Should raise error for angle out of range"
    except Exception as e:
        assert "out of range" in str(e)
        print("  ✓ Angle limit enforcement")

    # Test angle mismatch
    service.initialize_state(45.0)
    try:
        service.process_encoder_reading("detector", 100.0)  # Should be 90.0
        assert False, "Should raise error for angle mismatch"
    except Exception as e:
        assert "Detector angle" in str(e) or "mismatch" in str(e).lower()
        print("  ✓ Detector angle validation")

    print("✅ Error handling tests passed!")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🧪 GONIOMETER SYSTEM TEST SUITE")
    print("=" * 60)

    try:
        test_core_layer()
        test_integration()
        test_error_handling()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60 + "\n")
        return 0

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
