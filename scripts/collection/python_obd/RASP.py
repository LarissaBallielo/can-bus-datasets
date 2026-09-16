
class RASPstrategy():
    """
        SELECT THE MODE OF RASPBERRY PI USAGE USING THE STRATEGY DESIGN PATTERN
    """
    def __init__(self, strategy) -> None:
        self.strategy = strategy

    def run(self) -> None:
        self.strategy.run()