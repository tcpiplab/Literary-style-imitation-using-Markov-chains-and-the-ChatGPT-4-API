import argparse
import os
from transformers import pipeline
import sentiment_utilities
from chatGptApiCall import call_openai_api, test_openai_api
from config import Config
from log_config import configure_logger


def parse_args():
    # Create the argument parser
    parser = argparse.ArgumentParser(
        description="A command line tool to generate random phrases that imitate a literary style based on a training "
                    "training_corpus_filename.")

    # Add arguments
    # Add the optional input file argument
    parser.add_argument("-i", "--input-file",
                        help="Path to the input file. .txt or .pdf (optional)",
                        default=Config.TRAINING_CORPUS)
    # TODO: Create a command line option to specify a directory containing several related training_corpus_filename
    #  files.
    parser.add_argument("-r", "--raw-markov",
                        action="store_true",
                        help="Print the raw Markov result (optional)")
    parser.add_argument("-sc", "--similarity-check",
                        action="store_true",
                        help="Quantify how similar the output is to the original training_corpus_filename (optional)")
    parser.add_argument("-sw", "--seed-words",
                        help="Word(s) to seed the Markov search. "
                             "If not found in the original training_corpus_filename, it will be prepended to the "
                             "output. (optional)",
                        default=None)
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Enable verbose mode")
    parser.add_argument("-q", "--quiet",
                        action="store_true",
                        help="Disable logging completely")
    parser.add_argument("-l", "--length",
                        help="Approximate length of the output (optional)",
                        default=Config.RESULT_LENGTH)
    parser.add_argument("-m", "--max-tokens",
                        help="Maximum number of tokens to generate. If not specified, "
                             "it increases automatically if you specify length. (optional)",
                        default=Config.MAX_TOKENS)
    parser.add_argument("-st", "--similarity-threshold",
                        help="Floating point similarity threshold for the similarity check (optional)",
                        default=Config.SIMILARITY_THRESHOLD)
    parser.add_argument("-w", "--similarity-window",
                        help="Number of consecutive words in the sliding window used for the similarity check ("
                             "optional)",
                        default=Config.SIMILARITY_WINDOW)
    parser.add_argument("-n", "--number_of_responses",
                        help="Number of responses to generate. Higher number also increases temperature and increases "
                             "likelihood of repetition(optional)",
                        default=Config.NUM_OF_RESPONSES)
    parser.add_argument("-temp", "--temperature", help="Specify the AI temperature (creativity). "
                                                       "Float between 0 and 2.0 (optional)")
    parser.add_argument('--sentiment', action='store_true', help="Perform sentiment analysis on input data.")

    parser.add_argument("-nc", "--no-chat-gpt",
                        action="store_true",
                        help="Do not call the ChatGPT API. Print the raw Markov result instead. (optional)")

    parser.add_argument('--summarize', action='store_true',
                        help='Use this flag to summarize the input file')

    # Add an optional test argument to test the API call
    parser.add_argument("-t", "--test", action="store_true", help="Test the API call")

    return parser.parse_args()


def clamp(value, min_value, max_value):
    """
    Clamp a given value between a minimum and maximum value.

    Args:
        value (float): The value to be clamped.
        min_value (float): The lower bound for the clamped value.
        max_value (float): The upper bound for the clamped value.

    Returns:
        float: The clamped value limited to the range [min_value, max_value].
    """
    return max(min(value, max_value), min_value)


def summarize_text(text, summarizer, max_length=1024):
    """
    Summarizes a given text using a specified summarizer model.

    This function takes a text and splits it into paragraphs based on double line breaks.
    It then iterates over each paragraph and generates a summary using the provided summarizer model.
    The length of the summary is determined dynamically based on the length of the paragraph.
    The generated summaries are stored in a list and returned as a single string joined by newlines.

    Args:
        text (str): The input text to be summarized.
        summarizer: The summarizer model or function used to generate the summaries.
        max_length (int, optional): The maximum length of the summary. Defaults to 1024.

    Returns:
        str: A string containing the generated summaries joined by newlines.

    Note:
        The function assumes that the summarizer model or function accepts the following parameters:
        - paragraph (str): The input paragraph to be summarized.
        - max_length (int): The maximum length of the summary.
        - min_length (int): The minimum length of the summary.
        - do_sample (bool): Whether to use sampling during the summarization process.

    Raises:
        Any exceptions raised by the underlying summarizer model or function may propagate up to the caller.
    """

    paragraphs = text.split("\n\n")

    summaries = []
    for paragraph in paragraphs:
        # Ensure the max_length of the summary is always less than the length of the input
        paragraph_length = len(paragraph.split())
        max_length = max(2, min(50, paragraph_length // 2))

        # Ensure min_length is not larger than max_length
        min_length = min(max_length, max(2, max_length // 2))

        if paragraph_length > min_length:
            summary = summarizer(paragraph, max_length=max_length, min_length=min_length, do_sample=False)[0]
            summaries.append(summary['summary_text'])

    # return summaries
    return '\n'.join(summaries)


def main():
    args = parse_args()

    # If the user specified a test argument, call the test_openai_api() function
    if args.test:
        test_openai_api()
        return

    if args.input_file and args.summarize:
        if os.path.exists(args.input_file):
            print("Summarizing file: ", args.input_file)
            with open(args.input_file, 'r') as f:
                corpus_as_string = f.read()

            # summarizer = pipeline('summarization')
            # Explicitly specify the model to be used for summarization
            summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=-1)
            # summary = summarizer(corpus_as_string, max_length=50, min_length=25, do_sample=False)

            # Replace the summarization line in your main() function with a call to summarize_text()
            summary = summarize_text(corpus_as_string, summarizer)

            # print(summary[0]['summary_text'])
            # print(summary)
            print("Paragraph-level summaries: ", summary)

            # Create an overall summary
            overall_summary = summarizer(summary, max_length=50, min_length=25, do_sample=False)
            print("Overall summary: ", overall_summary[0]['summary_text'])

        else:

            print(f"No such file: {args.input_file}")

    # Update the config based on the parsed arguments
    Config.VERBOSE = args.verbose
    Config.QUIET = args.quiet
    Config.RESULT_LENGTH = int(args.length)
    # Adjust the max_tokens value based on the length
    # 1 token ~= 0.75 of a word, or about 4 characters
    Config.MAX_TOKENS = int(Config.RESULT_LENGTH * (4 / 3))

    # If the user specified a temperature value, update the config
    if args.temperature:
        Config.TEMPERATURE = float(args.temperature)

    # But if the user specified a max_tokens value, update the config
    if int(args.max_tokens) > Config.RESULT_LENGTH:
        Config.MAX_TOKENS = int(args.max_tokens)

    # If the user specified a similarity threshold, update the config
    if args.similarity_threshold:
        Config.SIMILARITY_THRESHOLD = float(args.similarity_threshold)

    # If the user specified a similarity window, update the config
    if args.similarity_window:
        Config.SIMILARITY_WINDOW = int(args.similarity_window)

    # If the user specified a number of responses, update the config
    if args.number_of_responses:

        Config.NUM_OF_RESPONSES = int(args.number_of_responses)

        # Adjust the temperature value based on the number of responses
        # Higher number also increases temperature and increases likelihood of repetition
        # Config.TEMPERATURE = Config.TEMPERATURE * 1.75

        if Config.NUM_OF_RESPONSES > 1:
            # Increase temperature proportionally to the number of responses or by any custom factor
            Config.TEMPERATURE += Config.NUM_OF_RESPONSES * 0.25

        # Clamp the temperature to be within the range [0, 2]
        Config.TEMPERATURE = clamp(Config.TEMPERATURE, 0, 2)

    configure_logger(__name__)

    if args.input_file is None:

        # If  the user specified a sentiment analysis, update the config and perform sentiment analysis
        if args.sentiment:
            Config.SENTIMENT = True

            print("Performing sentiment analysis on the training_corpus_filename...")
            sentiment_utilities.analyze_sentiment_of_file(Config.TRAINING_CORPUS)

        corrected_sentence = call_openai_api(Config.MAX_TOKENS,
                                             None,
                                             args.raw_markov,
                                             args.similarity_check,
                                             args.seed_words,
                                             args.no_chat_gpt)
        print(f">>>> {corrected_sentence}")
        # if Config.SENTIMENT:

        # sentiment_utilities.analyze_sentiment(corrected_sentence)

    else:
        # If  the user specified a sentiment analysis, update the config and perform sentiment analysis
        if args.sentiment:
            Config.SENTIMENT = True

            # Sentiment analysis is performed on the input file
            sentiment_utilities.analyze_sentiment_of_file(args.input_file)

        corrected_sentence = call_openai_api(Config.MAX_TOKENS, args.input_file, args.raw_markov, args.similarity_check,
                                             args.seed_words,
                                             args.no_chat_gpt)

        if args.sentiment:

            # Perform sentiment analysis on the output sentence
            sentiment_utilities.print_sentiment_analysis_results(corrected_sentence)


if __name__ == "__main__":
    main()
