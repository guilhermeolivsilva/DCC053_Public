from typing import Iterator

import enum
from Exp import *


class TokenType(enum.Enum):
    """Definitions of possible tokens to be considered."""

    EOF = -1  # End of file
    NLN = 0  # New line
    WSP = 1  # White Space
    NUM = 2  # Number (integers)
    LPR = 3  # Left parenthesis
    RPR = 4  # Right parenthesis
    ADD = 202  # The token '+'
    SUB = 203  # The token '-'
    MUL = 204  # The token '*'
    DIV = 205  # The token '/'


class Token:
    """
    This class represents a token, which is a basic unit of meaning extracted
    from the input string during lexical analysis.

    Attributes:
    -----------
    text : str
        The token's actual text, used for identifiers, strings, and numbers.
    kind : TokenType
        The type of the token, which classifies it based on its role in the
        expression.
    """

    # A list of tokens that represent operators in arithmetic expressions:
    operators = {TokenType.ADD, TokenType.SUB, TokenType.MUL, TokenType.DIV}

    def __init__(self, tokenText: str, tokenKind: TokenType) -> None:
        """
        Initialize a Token object with its text and type.

        Parameters:
        -----------
        tokenText : str
            The actual text of the token.
        tokenKind : TokenType
            The type of the token defined in TokenType.
        """

        self.text: str = tokenText
        self.kind: TokenType = tokenKind


class Lexer:
    """
    This class implements a simple lexer. It processes an input string and
    breaks it down into a sequence of tokens.

    The lexer maintains an internal state that tracks the current position in
    the input string. Each call to `getToken` returns the next token and
    advances the lexer state.

    Attributes:
    -----------
    input_string : str
        The string to be tokenized.
    position : int
        The current position in the input string.
    length : int
        The length of the input string.
    """

    def __init__(self, input_string: str) -> None:
        """
        Initialize the lexer with the input string that will be scanned.

        Parameters:
        -----------
        input_string : str
            The string to be tokenized.
        """

        self.input_string: str = input_string
        self.position: int = 0
        self.length: int = len(input_string)

    def next_valid_token(self) -> Token:
        """
        Retrieve the next valid token that is not a white space or a new line.

        This method skips any tokens that are classified as white space or new
        line and returns the first non-whitespace token found.

        Returns:
        --------
        token : Token
            The next valid token in the input stream.

        Example:
        --------
        >>> lexer = Lexer("1 2 +")
        >>> next_valid_token = lexer.next_valid_token()
        >>> print(vars(next_valid_token))
        {'text': '1', 'kind': <TokenType.NUM: 2>}

        >>> next_valid_token = lexer.next_valid_token()
        >>> print(vars(next_valid_token))
        {'text': '2', 'kind': <TokenType.NUM: 2>}

        >>> next_valid_token = lexer.next_valid_token()
        >>> print(vars(next_valid_token))
        {'text': '+', 'kind': <TokenType.ADD: 202>}
        """

        token = self.getToken()

        if token.kind in [TokenType.WSP, TokenType.NLN]:
            token = self.next_valid_token()

        return token

    def tokens(self) -> Iterator[Token]:
        """
        Get a generator that yields valid tokens from the input string, ignoring
        white spaces and new lines.

        This method continues to yield tokens until the end of the file is
        reached.

        Yields:
        -------
        token : Iterator[Token]
            The next valid token in the input stream.

        Example:
        --------
        >>> lexer = Lexer("1 2 +")
        >>> token_iterator = lexer.tokens()
        >>> print(vars(next(token_iterator)))
        {'text': '1', 'kind': <TokenType.NUM: 2>}

        >>> print(vars(next(token_iterator)))
        {'text': '2', 'kind': <TokenType.NUM: 2>}

        >>> print(vars(next(token_iterator)))
        {'text': '+', 'kind': <TokenType.ADD: 202>}
        """

        token = self.getToken()

        while token.kind != TokenType.EOF:
            if token.kind not in [TokenType.WSP, TokenType.NLN]:
                yield token

            token = self.getToken()

    def getToken(self):
        """
        Retrieve the next token from the input string.

        The lexer reads characters from the input string, classifies them
        according to their type (e.g., operator, number, white space), and
        returns a Token object.

        Returns:
        --------
        : Token
            The next token identified in the input string.

        Example:
        --------
        >>> lexer = Lexer("1 2 +")
        >>> token = lexer.getToken()
        >>> vars(token)
        {'text': '1', 'kind': <TokenType.NUM: 2>}

        >>> token = lexer.getToken()
        >>> vars(token)
        {'text': ' ', 'kind': <TokenType.WSP: 1>}

        >>> token = lexer.getToken()
        >>> vars(token)
        {'text': '2', 'kind': <TokenType.NUM: 2>}

        >>> token = lexer.getToken()
        >>> vars(token)
        {'text': ' ', 'kind': <TokenType.WSP: 1>}

        >>> token = lexer.getToken()
        >>> vars(token)
        {'text': '+', 'kind': <TokenType.ADD: 202>}

        Raises:
        -------
        ValueError
            Raised if the character is not associated with any known tokens.
        """

        if self.position >= self.length:
            return Token("", TokenType.EOF)

        current_char = self.input_string[self.position]
        self.position += 1

        if current_char.isdigit():
            # Handle numbers (NUM)
            number_text = current_char
            while (
                self.position < self.length
                and self.input_string[self.position].isdigit()
            ):
                number_text += self.input_string[self.position]
                self.position += 1

            return Token(number_text, TokenType.NUM)

        # Handle non-numeric tokens
        non_numeric_tokens: dict[str, int] = {
            "+": TokenType.ADD,
            "-": TokenType.SUB,
            "*": TokenType.MUL,
            "/": TokenType.DIV,
            "(": TokenType.LPR,
            ")": TokenType.RPR,
            " ": TokenType.WSP,
            "\n": TokenType.NLN,
        }

        if current_char not in non_numeric_tokens:
            raise ValueError(f"Unexpected character: {current_char}")

        return Token(current_char, non_numeric_tokens[current_char])


def compute_prefix(lexer: Lexer) -> Expression:
    """
    Converts an arithmetic expression in Polish Notation to an expression tree.

    This function converts a string into an expression tree, and returns it.

    Parameters:
    -----------
    lexer : Lexer
        An instance of the Lexer class, initialized with a string containing the
        arithmetic expression in prefix notation.

    Returns:
    --------
    : int
        The computed value of the arithmetic expression.

    Raises:
    -------
    ValueError
        Raised if an unexpected token type is encountered.

    Examples:
    ---------
    >>> lexer = Lexer("+ 3 * 4 2")
    >>> e = compute_prefix(lexer)
    >>> e.eval()
    11

    >>> lexer = Lexer("+ * 3 4 2")
    >>> e = compute_prefix(lexer)
    >>> e.eval()
    14
    """

    token = lexer.next_valid_token()

    if token.kind == TokenType.NUM:
        # Base case: return the value if it's a number
        return Num(int(token.text))

    elif token.kind in Token.operators:
        # Recursive case: evaluate the operands
        a = compute_prefix(lexer)
        b = compute_prefix(lexer)

        operations_map: dict[str, BinaryExpression] = {
            TokenType.ADD: Add,
            TokenType.SUB: Sub,
            TokenType.MUL: Mul,
            TokenType.DIV: Div,
        }

        operation = operations_map[token.kind]
        return operation(a, b)

    else:
        raise ValueError(f"Unexpected token type: {token.kind}")
