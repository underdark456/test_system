from src.options_providers.options_provider import OptionsProvider


def get_uhp():
    uhps = OptionsProvider.get_uhp(default=False)
    print(f'Number of UHP available: {len(uhps)}')
    for uhp in uhps:
        print(uhp)


if __name__ == '__main__':
    get_uhp()
