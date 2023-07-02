import random
from colorama import init, Fore, Style
from log_config import configure_logger
from config import Config

# Initialize colorama
init(autoreset=True)


class TextGenerator:

    # This class is used to generate training_corpus_filename from a given corpus file.

    # Initializes the class by configuring a logger with the current module's name
    # and enabling auto-reset for the terminal color output.
    def __init__(self):
        self.logger = configure_logger(__name__)
        init(autoreset=True)

    # This method is used to return the training_corpus_filename from a given corpus file.
    # The corpus file should be in UTF-8 format. But combining both the errors='replace' parameter
    # and the try/except block provides more robust error handling for
    # various issues that may arise when working with input files.
    @staticmethod
    def return_corpus_text(corpus_file_name):
        """
               Reads the content of a corpus file and returns it as a string.

               Args:
                   corpus_file_name (str): The path of the corpus file to be read.

               Returns:
                   str: The content of the corpus file as a string. If an error occurs while reading the file,
                        an empty string is returned and an error message is printed.

               Raises:
                   None
               """
        try:
            with open(corpus_file_name, encoding='utf-8', errors='replace') as content_file:
                corpus_as_string = content_file.read()

            return corpus_as_string

        except Exception as e:

            print(f"{Fore.RED}[-] Error while reading the corpus file '{corpus_file_name}': {e}{Style.RESET_ALL}")
            return ""

    #  This method is used to convert the list of words into a string from a given corpus file.
    @staticmethod
    def convert_word_list_to_string(final_output_word_list):
        return ' '.join(final_output_word_list)

    def generate_text(self, corpus_file_name, prefix_length, output_words_length, seed_words=None):
        """
        Generate random text based on the input corpus file content, given prefix and word lengths.

        This function reads the corpus file, cleans up the corpus string, applies a Markov algorithm to generate
        a list of output words, and then cleans up the output.

        :param corpus_file_name: The path to the input corpus file.
        :type corpus_file_name: str
        :param prefix_length: The length of the prefix as a tuple for the transition dictionary.
        :type prefix_length: int
        :param output_words_length: The number of words in the generated text.
        :type output_words_length: int
        :param seed_words: Initial words to seed the Markov algorithm. If None, the algorithm chooses initial words.
        :type seed_words: tuple, optional

        :returns: A list of words forming the generated text.
        :rtype: list
        """
        corpus_as_string = self.return_corpus_text(corpus_file_name)

        corpus_as_string = self.clean_up_corpus_string(corpus_as_string)

        output_word_list = self.markov_algorithm(corpus_as_string, output_words_length, prefix_length, seed_words)

        # TODO: Should this return the output_word_list?
        self.clean_up_markov_output(output_word_list)

        return output_word_list

    @staticmethod
    def clean_up_markov_output(output_word_list):
        # This method is used to clean up the output of the Markov algorithm.

        # Remove words that shouldn't be at the end of a sentence.
        if output_word_list[-1] in ["and", "i", "mr"]:
            output_word_list.pop()

        # Remove words that shouldn't be at the beginning of a sentence.
        if output_word_list[0] in ["and", "him"]:
            output_word_list.pop(0)

    def markov_algorithm(self, corpus_as_string, output_words_length, prefix_length, seed_words):
        """
            Generate a list of output words using a Markov chain algorithm.

            The function processes the input corpus string to create a dictionary of sequences and their next words.
            It then uses the Markov chain algorithm to generate a sequence of words.

            :param corpus_as_string: The input corpus as a single string.
            :type corpus_as_string: str
            :param output_words_length: The number of words to generate.
            :type output_words_length: int
            :param prefix_length: The length of the prefix for the Markov chain to predict the next word.
            :type prefix_length: int
            :param seed_words: Initial words to seed the Markov chain. Optional.
            :type seed_words: tuple

            :returns: A list of words forming the generated text.
            :rtype: list
            """

        # prefix_length determines which order of Markov
        # meaning how many words to look backwards to predict the next word.
        chain = {tuple(['.'] * prefix_length): [' ']}

        # Iterate through the corpus and create a dictionary of sequences and their next words.
        for i in range(len(corpus_as_string) - prefix_length):

            # the variable seq holds a tuple of characters, representing the sequence of length prefix_length
            # starting at index i in the input string corpus_as_string.
            seq = tuple(corpus_as_string[i: i + prefix_length])

            # Initialize an empty list as the value for a new seq key in the chain dictionary
            # if it doesn't already exist.
            if seq not in chain:
                chain[seq] = []

            # If the next word is not a period, add it to the chain.
            chain[seq].append(corpus_as_string[i + prefix_length] if i + prefix_length < len(corpus_as_string) else '.')

        if seed_words is not None:
            start_seq = tuple(seed_words.split())
        else:
            start_seq = random.choice(list(chain.keys()))
        output_word_list = list(start_seq)
        current_seq = start_seq
        for i in range(output_words_length):
            try:
                next_word = random.choice(chain[current_seq])
            except KeyError:
                if Config.VERBOSE:
                    not_found_message = (
                        f"The exact seed word sequence {Fore.RED}"
                        f"'{seed_words}'"
                        f"{Style.RESET_ALL} was not found in the original corpus."
                    )
                    self.logger.warning(f"{not_found_message}")
                current_seq = random.choice(list(chain.keys()))
                next_word = random.choice(chain[current_seq])

            current_seq = tuple((list(current_seq) + [next_word])[1:])
            output_word_list.append(next_word)
        return output_word_list

    @staticmethod
    def clean_up_corpus_string(corpus_as_string):
        """
        Cleans up the input corpus string by converting to lowercase, replacing special characters, and splitting
        into a list of words.

        This method processes the input string to convert all characters to lowercase, replace punctuation
        with spaces, remove certain characters, and split the string into a list of words.

        :param corpus_as_string: The input corpus as a single string.
        :type corpus_as_string: str

        :returns: The cleaned up corpus as a list of words.
        :rtype: list
        """
        corpus_as_string = corpus_as_string.lower()
        for char in ["!", ".", ",", "@", "&", "?", "-"]:
            corpus_as_string = corpus_as_string.replace(char, " ")
        for char in ['"', '(', ')']:
            corpus_as_string = corpus_as_string.replace(char, "")
        corpus_as_string = corpus_as_string.split()
        return corpus_as_string
