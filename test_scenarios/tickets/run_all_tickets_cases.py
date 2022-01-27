import test_scenarios.tickets.subtests as subtests
from src.injection_container import InjectionContainer

option_path = "test_scenarios.tickets"

if __name__ == '__main__':
    loader = InjectionContainer.get_loader(option_path)
    suite = loader.loadTestsFromModule(subtests)
    runner = InjectionContainer.get_runner(option_path)
    a = runner.run(suite)

