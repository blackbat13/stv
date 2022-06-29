import click
import time
import stv.models.asynchronous.template_parser as template_parser
from stv.models import TianJiModel, CastleModel, BridgeModel


@click.group()
def run():
    pass


@run.group()
def verify():
    pass


@verify.group()
def synchronous():
    pass


def verify_synchronous(model_generator, imperfect: bool):
    click.echo("Generating model")

    time_start = time.perf_counter()
    model_generator.generate()
    time_end = time.perf_counter()

    click.echo(f"Model generated in {time_end - time_start} seconds")
    click.echo("Starting verification")

    if imperfect:
        click.echo("Imperfect information")
        time_start = time.perf_counter()
        atl_model = model_generator.model.to_atl_imperfect()
        time_end = time.perf_counter()
    else:
        click.echo("Perfect information")
        time_start = time.perf_counter()
        atl_model = model_generator.model.to_atl_perfect()
        time_end = time.perf_counter()

    click.echo(f"Formula verified in {time_end - time_start} seconds")
    winning = model_generator.get_model_winning_states()

    result = atl_model.minimum_formula_many_agents([0], winning)

    if 0 in result:
        click.echo("Approximation result: True")
    else:
        click.echo("Approximation result: False")


@synchronous.command()
@click.option('--horses', type=int, prompt='Number of horses', help='number of horses')
@click.option('--imperfect', is_flag=True, help='imperfect information')
def tianji(horses: int, imperfect: bool):
    click.echo(f"TianJi model, {horses} horses")
    tian_ji_model = TianJiModel(horses)
    verify_synchronous(tian_ji_model, imperfect)


@synchronous.command()
@click.option('--cards', type=int, prompt='Number of cards', help='number of cards')
@click.option('--imperfect', is_flag=True, help='imperfect information')
def bridge(cards: int, imperfect: bool):
    click.echo(f"Bridge model, {cards} cards")
    hands = BridgeModel.generate_random_hands(cards, cards)
    click.echo(f"Generated hands: {BridgeModel.hands_to_readable_hands(hands)}")
    bridge_model = BridgeModel(cards, cards, {'board': [-1, -1, -1, -1], 'lefts': [0, 0],
                                              'hands': hands, 'next': 0, 'history': [],
                                              'beginning': 0, 'clock': 0, 'suit': -1})
    verify_synchronous(bridge_model, imperfect)


@synchronous.command()
@click.option('--w1', type=int, prompt='Number of workers for the first castle', help='first castle workers')
@click.option('--w2', type=int, prompt='Number of workers for the second castle', help='second castle workers')
@click.option('--w3', type=int, prompt='Number of workers for the third castle', help='third castle workers')
@click.option('--life', default=3, type=int, prompt='Castle life', help='castle life')
@click.option('--imperfect', is_flag=True, help='imperfect information')
def castles(w1: int, w2: int, w3: int, life: int, imperfect: bool):
    click.echo(f"Castles ({w1},{w2},{w3}), life={life}")
    castle_model = CastleModel([w1, w2, w3], [life, life, life])
    verify_synchronous(castle_model, imperfect)


@verify.command()
def asynchronous():
    click.echo("Verify asynchronous - not implemented yet")


@run.group()
def generate_spec():
    pass


@generate_spec.command()
@click.option('--n_ai', default=2, prompt='Number of AI agents', help='number of AI agents')
@click.option('--max_model_quality', default=2, prompt='Maximum model quality', help='maximum model quality')
def sai(n_ai, max_model_quality):
    input_filename, output_filename, config = template_parser.sai(n_ai, max_model_quality)
    path = template_parser.save_to_file(input_filename, output_filename, config)
    click.echo(f"Model spec saved to {path}")

@generate_spec.command()
@click.option('--n_ai', default=2, prompt='Number of AI agents', help='number of AI agents')
@click.option('--max_model_quality', default=2, prompt='Maximum model quality', help='maximum model quality')
@click.option('--imp', default=1, prompt='Impersonator id', help='impersonator id')
def sai_imp(n_ai, max_model_quality, imp):
    input_filename, output_filename, config = template_parser.sai_imp(n_ai, max_model_quality, imp)
    path = template_parser.save_to_file(input_filename, output_filename, config)
    click.echo(f"Model spec saved to {path}")


if __name__ == "__main__":
    run()
