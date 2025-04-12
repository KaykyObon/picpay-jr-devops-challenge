const root = document.querySelector("#root");

const home = () => {
    const container = document.createElement('div');
    container.innerHTML = `<h2>Home</h2>`;

    const readerp = document.createElement('p');
    const writerp = document.createElement('p');
    container.appendChild(readerp);
    container.appendChild(writerp);

    readerhealth(readerp);
    writerhealth(writerp);
    container.classList.add("mx-auto", "align-middle", "container");

    return container;
};

const reader = () => {
    const container = document.createElement('div');
    container.innerHTML = `<h2>Reader Screen</h2>`;

    const child = document.createElement('p');
    container.appendChild(child);

    readData(child);
    container.classList.add("mx-auto", "align-middle", "container");

    // Atualiza a cada 2 segundos
    const refresh = setInterval(() => {
        readData(child);
    }, 2000);

    return container;
};

const writer = () => {
    const container = document.createElement('div');
    container.innerHTML = `
        <h2>Writer Screen</h2>
        <form id="submitdata" role="form">
          <div class="form-group">
            <label for="text">Key Content:</label>
            <input type="text" class="form-control" id="post">
          </div>
          <button type="submit" class="btn btn-default">Enviar</button>
        </form>
    `;
    container.classList.add("mx-auto", "align-middle", "container");

    const formsubmit = container.querySelector("#submitdata");
    formsubmit.addEventListener('submit', writeData);

    return container;
};

const readerhealth = (readerparagraph) => {
    const url = 'http://localhost:8080/health';
    fetch(url, {
        method: "GET",
        mode: 'cors',
    })
    .then(response => response.text())
    .then(body => {
        assembleStatus(readerparagraph, "Reader", body);
    })
    .catch(error => {
        console.log(error);
        assembleStatus(readerparagraph, "Reader", "down");
    });
};

const writerhealth = (writerparagraph) => {
    const url = 'http://localhost:8081/health';
    fetch(url, {
        method: "GET",
        mode: 'cors',
    })
    .then(response => response.text())
    .then(body => {
        assembleStatus(writerparagraph, "Writer", body);
    })
    .catch(error => {
        console.log(error);
        assembleStatus(writerparagraph, "Writer", "down");
    });
};

const assembleStatus = (paragraph, service, status) => {
    const statusBadge = status === "up" ? "success" : "danger";
    paragraph.innerHTML = `${service} service status <span class="badge badge-${statusBadge}">${status}</span>`;
};

async function writeData(e) {
    e.preventDefault();

    const input = e.target.elements.post.value;
    const url = 'http://localhost:8081/write';

    fetch(url, {
        method: "POST",
        mode: "cors",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(input),
    })
    .then(response => {
        if (!response.ok) throw new Error("Erro ao enviar dados");
        return response.text();
    })
    .then(data => console.log("Sucesso:", data))
    .catch(error => console.log("Erro:", error));
}

const readData = (paragraph) => {
    const url = 'http://localhost:8080/data';
    fetch(url, {
        method: "GET",
        mode: 'cors',
    })
    .then(response => response.text())
    .then(body => {
        paragraph.innerHTML = "Valor encontrado = " + body;
    })
    .catch(error => {
        console.log(error);
        paragraph.innerHTML = `
            <div class="alert alert-warning" role="alert">
              Ocorreu um erro ao buscar a chave
            </div>`;
    });
};

const routes = {
    home: home,
    reader: reader,
    writer: writer,
};

const validateHash = (hash) => (hash === "" ? 'home' : hash.replace('#', ''));

const renderPage = () => {
    const page = validateHash(window.location.hash);
    root.innerHTML = '';
    const component = routes[page];
    if (component) {
        root.appendChild(component());
    } else {
        root.innerHTML = `<h2>Página não encontrada</h2>`;
    }
};

const init = () => {
    window.addEventListener('hashchange', renderPage);
    renderPage();
};

window.addEventListener('load', init);