import numpy as np 
import pandas as pd
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler

class GRUD(nn.Module):
    def __init__(self, input_size, hidden_size):
        super(GRUD, self).__init__()
        self.hidden_size = hidden_size

        self.gamma_x = nn.Parameter(torch.Tensor(input_size))
        self.gamma_h = nn.Parameter(torch.Tensor(hidden_size))

        self.embedding = nn.Linear(input_size * 2, input_size)
        self.gru_cell = nn.GRUCell(input_size, hidden_size)
        self.output_layer = nn.Linear(hidden_size, input_size)
        self.softplus = nn.Softplus()

        self.reset_parameters()

    def reset_parameters(self):
        nn.init.normal_(self.gamma_x, mean=0, std=0.1)
        nn.init.normal_(self.gamma_h, mean=0, std=0.1)
        nn.init.xavier_uniform_(self.embedding.weight)
        nn.init.xavier_uniform_(self.output_layer.weight)

    def forward(self, x, x_last_obs, mask, delta_t_x, delta_t_h, h):
        gamma_x = torch.exp(-torch.relu(self.gamma_x) * delta_t_x)
        gamma_h = torch.exp(-torch.relu(self.gamma_h) * delta_t_h.unsqueeze(-1))

        x = mask * x + (1 - mask) * (gamma_x * x_last_obs)
        h = gamma_h * h

        x_combined = torch.cat([x, mask], dim=-1)
        x_emb = self.embedding(x_combined)
        h = self.gru_cell(x_emb, h)

        # Aplicar Softplus para asegurar salidas positivas
        x_imputed = self.softplus(self.output_layer(h))

        return h, x_imputed

def _process_data_multivariate(data):
    values = data.values
    num_features = values.shape[1]
    time = data.index.astype(np.int64) // 10**9  # Timestamps en segundos
    time = time.values

    mask = ~np.isnan(values)
    mask = mask.astype(float)

    values_filled = np.nan_to_num(values)

    x_last_obs = np.zeros_like(values)
    delta_t_x = np.zeros_like(values)
    delta_t_h = np.zeros(len(time))

    for i in range(num_features):
        first_obs_idx = np.where(mask[:, i] == 1)[0]
        if len(first_obs_idx) > 0:
            first_idx = first_obs_idx[0]
            x_last_obs[first_idx, i] = values_filled[first_idx, i]
        else:
            first_idx = 0

    for i in range(1, len(time)):
        delta = time[i] - time[i - 1]
        delta_t_h[i] = delta

        for j in range(num_features):
            if mask[i - 1, j]:
                x_last_obs[i, j] = values_filled[i - 1, j]
                delta_t_x[i, j] = delta
            else:
                x_last_obs[i, j] = x_last_obs[i - 1, j]
                delta_t_x[i, j] = delta_t_x[i - 1, j] + delta

    delta_t_x = delta_t_x / delta_t_x.max()
    delta_t_h = delta_t_h / delta_t_h.max()

    return values_filled, mask, delta_t_x, delta_t_h, x_last_obs


def _prepare_data(data_serie):
    # 1. Preparación de los Datos
    tmp_data = data_serie.copy()
    tmp_data['Date'] = pd.to_datetime(dict(year=tmp_data.Year, month=tmp_data.Month, day=1))
    tmp_data.sort_values('Date', inplace=True)
    tmp_data.set_index('Date', inplace=True)
    tmp_data.drop(['Year', 'Month'], axis=1, inplace=True)

    # 2. Normalización de los Datos
    scaler = MinMaxScaler()
    x_np = tmp_data.values
    x_scaled = scaler.fit_transform(x_np)
    data_scaled = pd.DataFrame(x_scaled, index=tmp_data.index, columns=tmp_data.columns)

    # 3. Procesamiento de los Datos
    values_filled, mask, delta_t_x, delta_t_h, x_last_obs = _process_data_multivariate(data_scaled)

    return values_filled, mask, delta_t_x, delta_t_h, x_last_obs, scaler, tmp_data.index, tmp_data.columns


def _train_grud(values_filled, mask, delta_t_x, delta_t_h, x_last_obs, hidden_size):
    # Convertir a tensores
    t_x = torch.tensor(values_filled, dtype=torch.float32)
    t_mask = torch.tensor(mask, dtype=torch.float32)
    t_delta_t_x = torch.tensor(delta_t_x, dtype=torch.float32)
    t_delta_t_h = torch.tensor(delta_t_h, dtype=torch.float32)
    t_x_last_obs = torch.tensor(x_last_obs, dtype=torch.float32)

    # 5. Configuración del Modelo y Entrenamiento
    input_size = t_x.shape[1]

    model = GRUD(input_size, hidden_size)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    epochs = 100
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()

        h = torch.zeros(1, hidden_size)
        loss = 0

        for t in range(len(t_x)):
            h, x_imputed = model(
                t_x[t].unsqueeze(0),
                t_x_last_obs[t].unsqueeze(0),
                t_mask[t].unsqueeze(0),
                t_delta_t_x[t].unsqueeze(0),
                t_delta_t_h[t].unsqueeze(0),
                h
            )
            loss += criterion(
                x_imputed * (1 - t_mask[t].unsqueeze(0)),
                t_x[t].unsqueeze(0) * (1 - t_mask[t].unsqueeze(0))
            )

        loss.backward()
        optimizer.step()

        if (epoch + 1) % 1 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")
    
    return model, t_x, t_mask, t_delta_t_x, t_delta_t_h, t_x_last_obs


def _impute_grud(model, x, mask, delta_t_x, delta_t_h, x_last_obs, scaler, data_index, data_columns, hidden_size):
    model.eval()
    with torch.no_grad():
        h = torch.zeros(1, hidden_size)
        imputations = []
        for t in range(len(x)):
            h, x_imputed = model(
                x[t].unsqueeze(0),
                x_last_obs[t].unsqueeze(0),
                mask[t].unsqueeze(0),
                delta_t_x[t].unsqueeze(0),
                delta_t_h[t].unsqueeze(0),
                h
            )
            x_filled = x[t].clone()
            x_filled[mask[t] == 0] = x_imputed.squeeze(0)[mask[t] == 0]
            imputations.append(x_filled.numpy())

    imputed_values = np.array(imputations)

    # Invertir la escala de las imputaciones
    imputed_values_rescaled = scaler.inverse_transform(imputed_values)
    imputed_data = pd.DataFrame(imputed_values_rescaled, index=data_index, columns=data_columns)

    return imputed_data


def grud_imputation(data_serie, hidden_size=32):
    values_filled, mask, delta_t_x, delta_t_h, x_last_obs, scaler, data_index, data_columns = _prepare_data(data_serie)
    model, x, mask, delta_t_x, delta_t_h, x_last_obs = _train_grud(values_filled, mask, delta_t_x, delta_t_h, x_last_obs, hidden_size)
    return _impute_grud(model, x, mask, delta_t_x, delta_t_h, x_last_obs, scaler, data_index, data_columns, hidden_size)
    