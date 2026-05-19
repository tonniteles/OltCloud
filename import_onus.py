import logging
import time

import API_OltCloud

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

SYNC_INTERVAL_SECONDS = 120
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 30

api = API_OltCloud.OltCloudAPI()

while True:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            onts = api.get_all_onts()
            API_OltCloud.write_onts_list(onts)
            logging.info("Lista de ONUs atualizada (%d registos)", len(onts))
            break
        except Exception:
            logging.exception(
                "Erro ao sincronizar ONUs (tentativa %d/%d)",
                attempt,
                MAX_RETRIES,
            )
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                logging.error("Sincronização falhou após %d tentativas", MAX_RETRIES)

    time.sleep(SYNC_INTERVAL_SECONDS)
