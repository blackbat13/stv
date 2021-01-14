# import stv.gui_helper.run_tian_ji
import sys

if __name__ == "__main__":
    model = sys.argv[1]
    method = sys.argv[2]
    if model == 'tian_ji':
        if method == 'run':
            import stv.gui_helper.run_tian_ji
        elif method == 'verify':
            import stv.gui_helper.verify_tian_ji
        elif method == 'domino':
            import stv.gui_helper.domino_tian_ji
    elif model == 'bridge':
        if method == 'run':
            import stv.gui_helper.run_bridge
        elif method == 'verify':
            import stv.gui_helper.verify_bridge
        elif method == 'domino':
            import stv.gui_helper.domino_bridge
    elif model == 'castles':
        if method == 'run':
            import stv.gui_helper.run_castles
        elif method == 'verify':
            import stv.gui_helper.verify_castles
        elif method == 'domino':
            import stv.gui_helper.domino_castles
    elif model == 'drone':
        if method == 'run':
            import stv.gui_helper.run_drone
        elif method == 'verify':
            import stv.gui_helper.verify_drone
        elif method == 'domino':
            import stv.gui_helper.domino_drone
    elif model == 'voting':
        if method == 'run':
            import stv.gui_helper.run_simple_voting
        elif method == 'verify':
            import stv.gui_helper.verify_simple_voting
        elif method == 'domino':
            import stv.gui_helper.domino_simple_voting
    elif model == 'global':
        if method == 'run':
            import stv.gui_helper.asynchronous.run_global
        elif method == 'verify':
            import stv.gui_helper.asynchronous.verify_global
        elif method == 'domino':
            import stv.gui_helper.asynchronous.domino_global
    elif model == 'bisimulation':
        if method == 'run':
            import stv.gui_helper.asynchronous.run_bisimulation
        elif method == 'verify':
            import stv.gui_helper.asynchronous.verify_bisimulation
        elif method == 'domino':
            import stv.gui_helper.asynchronous.domino_bisimulation
        elif method == "check":
            import stv.gui_helper.asynchronous.check_bisimulation
