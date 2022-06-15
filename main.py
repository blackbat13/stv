import click
import time
import stv.models.asynchronous.template_parser as template_parser
from stv.models import TianJiModel


@click.group()
def run():
    pass


@run.group()
def verify():
    pass


@verify.group()
def synchronous():
    pass


@synchronous.command()
@click.option('--horses', type=int, prompt="Number of horses", help='number of horses')
@click.option('--imperfect', is_flag=True, help='imperfect information')
def tianji(horses: int, imperfect: bool):
    click.echo(f"TianJi model, {horses} horses")
    tian_ji_model = TianJiModel(horses)

    click.echo("Generating model")

    time_start = time.perf_counter()
    tian_ji_model.generate()
    time_end = time.perf_counter()

    click.echo(f"Model generated in {time_end - time_start} seconds")
    click.echo("Starting verification")

    if imperfect:
        click.echo("Imperfect information")
        time_start = time.perf_counter()
        atl_model = tian_ji_model.model.to_atl_imperfect()
        time_end = time.perf_counter()
    else:
        click.echo("Perfect information")
        time_start = time.perf_counter()
        atl_model = tian_ji_model.model.to_atl_perfect()
        time_end = time.perf_counter()

    click.echo(f"Formula verified in {time_end - time_start} seconds")
    winning = tian_ji_model.get_winning_states("")

    result = atl_model.minimum_formula_many_agents([0], winning)

    if 0 in result:
        click.echo("Approximation result: True")
    else:
        click.echo("Approximation result: False")


@verify.command()
def asynchronous():
    click.echo("Verify asynchronous - not implemented yet")


@run.group()
def generate_spec():
    pass


@generate_spec.command()
@click.option('--n_ai', default=2, help='number of AI agents')
@click.option('--max_model_quality', default=2, help='maximum model quality')
def sai(n_ai, max_model_quality):
    input_filename, output_filename, config = template_parser.sai(n_ai, max_model_quality)
    path = template_parser.save_to_file(input_filename, output_filename, config)
    click.echo(f"Model spec saved to {path}")


if __name__ == "__main__":
    run()
