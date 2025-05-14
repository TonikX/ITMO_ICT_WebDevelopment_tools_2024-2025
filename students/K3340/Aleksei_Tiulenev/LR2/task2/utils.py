class ColorLog:
    RESET = "\033[0m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"

    @staticmethod
    def blue(text: str) -> str:
        return f"{ColorLog.BLUE}{text}{ColorLog.RESET}"

    @staticmethod
    def green(text: str) -> str:
        return f"{ColorLog.GREEN}{text}{ColorLog.RESET}"

    @staticmethod
    def yellow(text: str) -> str:
        return f"{ColorLog.YELLOW}{text}{ColorLog.RESET}"
