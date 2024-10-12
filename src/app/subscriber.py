import time
import pika
import sys
import concurrent.futures

from controller.hpa.hpa_controller import HPA
from controller.fuzzy.fuzzy_controller import FuzzyController
from controller.AsTAR.AsTAR import AsTAR
from controller.rules.rules_generator import GeneticAlgorithm
from utils.core_functions import save_data_to_csv
from shared.shared import (
    PREFETCH_COUNT,
    SERVER_IP,
    QUEUE_NAME
)

VARIABLE_SETPOINTS = [500, 1500, 1000, 600, 2100]
FIXED_SETPOINTS = [1000]


def run_genetic_algorithm(fuzzy_controller: FuzzyController):
    ga = GeneticAlgorithm()
    best_rule_set = ga.improve_rules()
    fuzzy_controller.update_rules(best_rule_set)
    print("Updated Fuzzy Controller with new rules.")
    print(f"New rules: {best_rule_set}")
    time.sleep(2)
    return best_rule_set


def update_fuzzy_controller_parallel(fuzzy_controller: FuzzyController):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_genetic_algorithm, fuzzy_controller)


if __name__ == "__main__":
    # Check for the arq_name argument
    if len(sys.argv) < 4:
        print("Usage: python subscriber.py <controller_name> <arq_name> <deffuzification_method>")
        sys.exit(1)

    controller_type = sys.argv[1]
    arq_name = sys.argv[2]
    deffuzification_method = sys.argv[3]

    if controller_type == "hpa":
        controller = HPA(max_value=25, min_value=1)
    elif controller_type == "astar":
        controller = AsTAR(max_value=25, min_value=1, hysteresis_band=150)
    elif controller_type == "fuzzy1":
        print(f"Starting a controller with type {controller_type} and deffuz {deffuzification_method}")
        controller = FuzzyController(type=1, defuzzification_method=deffuzification_method)
    elif controller_type == "fuzzy2":
        print(f"Starting a controller with type {controller_type} and deffuz {deffuzification_method}")
        controller = FuzzyController(type=2, defuzzification_method=deffuzification_method)
    elif controller_type == "fuzzy3":
        print(f"Starting a controller with type {controller_type} and deffuz {deffuzification_method}")
        controller = FuzzyController(type=3, defuzzification_method=deffuzification_method)
    elif controller_type == "fuzzy4":
        print(f"Starting a controller with type {controller_type} and deffuz {deffuzification_method}")
        controller = FuzzyController(type=4, defuzzification_method=deffuzification_method)
    elif controller_type == "fuzzy5":
        print(f"Starting a controller with type {controller_type} and deffuz {deffuzification_method}")
        controller = FuzzyController(type=5, defuzzification_method=deffuzification_method)
    elif controller_type == "fuzzy6":
        print(f"Starting a controller with type {controller_type} and deffuz {deffuzification_method}")
        controller = FuzzyController(type=6, defuzzification_method=deffuzification_method)
        
    consuming_time = 0
    count_messages = 0
    sample_id = 1

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(SERVER_IP)
    )
    channel = connection.channel()
    prefetch_count = PREFETCH_COUNT
    channel.queue_declare(queue=QUEUE_NAME)
    channel.basic_qos(prefetch_count=prefetch_count)

    print(f"Started consuming messages from queue '{QUEUE_NAME}'")
    continue_consuming = True
    while continue_consuming:
        try:
            for method, properties, body in channel.consume(queue=QUEUE_NAME, inactivity_timeout=1):
                if consuming_time == 0:
                    consuming_time = time.time()

                if body is not None:
                    # Process the message
                    count_messages += 1

                    channel.basic_ack(method.delivery_tag)
                    time_passed = time.time() - consuming_time
                    if time_passed >= 10:
                        channel.cancel()
                        print("Consumer stopped to save metrics.")
                        arrival_rate=count_messages / time_passed
                        save_data_to_csv(
                            arq_name=arq_name,
                            prefetch_count=prefetch_count,
                            arrival_rate=arrival_rate,
                            sample_number=sample_id,
                            setpoint=VARIABLE_SETPOINTS[0]
                        )
                        print(f"""
                            Sample {sample_id}:
                            Prefetch count: {prefetch_count}
                            Arrival rate: {arrival_rate}
                            Setpoint: {VARIABLE_SETPOINTS[0]}
                        """)
                        # Evaluate new prefetch count
                        new_prefetch_count = controller.evaluate_new_prefetch_count(
                            prefetch_count,
                            arrival_rate,
                            VARIABLE_SETPOINTS[0]
                        )
                        channel.basic_qos(prefetch_count=new_prefetch_count)
                        if sample_id % 50 == 0:
                            VARIABLE_SETPOINTS.pop(0)
                        if len(VARIABLE_SETPOINTS) == 0:
                            continue_consuming = False
                            break
                        sample_id += 1
                        consuming_time = 0
                        count_messages = 0
                        prefetch_count = new_prefetch_count
        except pika.exceptions.ChannelClosedByBroker:
            print("Channel was closed by broker. Continuing to next iteration.")
            break
